import math
import statistics
import warnings

import numpy as np
from hmmlearn.hmm import GaussianHMM
from sklearn.model_selection import KFold
from asl_utils import combine_sequences


class ModelSelector(object):
    '''
    base class for model selection (strategy design pattern)
    '''

    def __init__(self, all_word_sequences: dict, all_word_Xlengths: dict, this_word: str,
                 n_constant=3,
                 min_n_components=2, max_n_components=10,
                 random_state=14, verbose=False):
        self.words = all_word_sequences
        self.hwords = all_word_Xlengths
        self.sequences = all_word_sequences[this_word]
        self.X, self.lengths = all_word_Xlengths[this_word]
        self.this_word = this_word
        self.n_constant = n_constant
        self.min_n_components = min_n_components
        self.max_n_components = max_n_components
        self.random_state = random_state
        self.verbose = verbose

    def select(self):
        raise NotImplementedError

    def base_model(self, num_states):
        # with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        # warnings.filterwarnings("ignore", category=RuntimeWarning)
        try:
            hmm_model = GaussianHMM(n_components=num_states, covariance_type="diag", n_iter=1000,
                                    random_state=self.random_state, verbose=False).fit(self.X, self.lengths)
            if self.verbose:
                print("model created for {} with {} states".format(self.this_word, num_states))
            return hmm_model
        except:
            if self.verbose:
                print("failure on {} with {} states".format(self.this_word, num_states))
            return None


class SelectorConstant(ModelSelector):
    """ select the model with value self.n_constant

    """

    def select(self):
        """ select based on n_constant value

        :return: GaussianHMM object
        """
        best_num_components = self.n_constant
        return self.base_model(best_num_components)


class SelectorBIC(ModelSelector):
    """ select the model with the lowest Bayesian Information Criterion(BIC) score

    http://www2.imm.dtu.dk/courses/02433/doc/ch6_slides.pdf
    Bayesian information criteria: BIC = -2 * logL + p * logN
    """
    # Pseudocode from https://discussions.udacity.com/t/how-to-start-coding-the-selectors/476905
    # Iterate from min number of components to max number of n_components
    # Create a model for each number of components in the loop
    # Fit the model with the current word
    # Get the lowest score (log likelihood)
    # Need parameters = n_components ** 2 + n_components * n_features - 1
    # Evalute the result for each number of components and get the lowest
    # Return model with lowest score

    # Create helper functions


    def select(self):
        """ select the best model for self.this_word based on
        BIC score for n between self.min_n_components and self.max_n_components

        :return: GaussianHMM object
        """
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        # Initialize list of BIC scores
        bic_scores = []
        # Initialize list of models
        models = []

        # Loop through range of components
        for n in range(self.min_n_components, self.max_n_components + 1):
            try:
                # Fit data to model and calculate logL score
                model = self.base_model(n)
                logL = model.score(self.X, self.lengths)
                # Determine number of samples
                N = len(self.X[0])
                # Determin number of parameters
                p = np.power(n, 2) + n * N - 1
                # Calculate BIC score
                bic = -2 * logL + p * np.log(N)
                # Updated corresponding lists
                bic_scores.append(bic)
                models.append(model)
            except:
                pass

        # Check if there are scores to consider
        if bic_scores:
            best_idx = bic_scores.index(max(bic_scores))
            return models[best_idx]
        else:
            # If no score available return None
            return None




class SelectorDIC(ModelSelector):
    ''' select best model based on Discriminative Information Criterion

    Biem, Alain. "A model selection criterion for classification: Application to hmm topology optimization."
    Document Analysis and Recognition, 2003. Proceedings. Seventh International Conference on. IEEE, 2003.
    http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.58.6208&rep=rep1&type=pdf
    https://pdfs.semanticscholar.org/ed3d/7c4a5f607201f3848d4c02dd9ba17c791fc2.pdf
    DIC = log(P(X(i)) - 1/(M-1)SUM(log(P(X(all but i))
    '''
    # Pseudocode from https://discussions.udacity.com/t/how-to-start-coding-the-selectors/476905
    # Fit model with word data
    # Get this word model score
    # Get component score: this_word_score - (sum(other words score) / total_word_qty -1)
    # Keep model with the number of compnents resulting in highest score

    def select(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        # Initialize list of other words
        other_words = []
        # Loop through words
        for word in self.words:
            # Update list of other words
            if word != self.this_word:
                other_words.append(self.hwords[word])

        # Initialize lists of logLs and models
        logLs = []
        models = []

        # Loop through range of components
        for n in range(self.min_n_components, self.max_n_components + 1):
            try:
                # Fit model and calculate logL
                model = self.base_model(n)
                logL = model.score(self.X, self.lengths)
                # Update logL and model lists
                logLs.append(logL)
                models.append(model)
            except:
                pass

        # Initialize list for DIC scores
        dic_scores = []
        # Loop through logLs
        for i in range(len(logLs)):
            # Calculate scores for other words
            other_word_scores = [models[i].score(word[0], word[1]) for word in other_words]
            # Update DIC scores list
            dic_scores.append(logLs[i] - (sum(other_word_scores)/len(other_word_scores) - 1))

        # Check for DIC score and find maximum
        if dic_scores:
            best_idx = dic_scores.index(max(dic_scores))
            return models[best_idx]
        else:
            return None


class SelectorCV(ModelSelector):
    ''' select best model based on average log Likelihood of cross-validation folds

    '''
    # Pseudocode from https://discussions.udacity.com/t/how-to-start-coding-the-selectors/476905
    # Split data into train and test sets
    # Use training data to fit model
    # Use test data to score model
    # Get average score
    # Keep number of components with largest average
    # Return model fitted over all data with best number of n_components

    def select(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        # logging.debug("Sequences: %r" % self.sequences)

        # Initialize KFold splits
        kf = KFold(n_splits = 3, shuffle = False, random_state = None)
        # Intialize lists for logLs, means, and models
        logLs = []
        means = []
        models = []

        # Loop through number of components
        for num_states in range(self.min_n_components, self.max_n_components + 1):
            try:
                # Make sure to have enough for minmum n_splits = 3
                if len(self.sequences) > 2:
                    # Loop through KFold train and test splits
                    for train_index, test_index in kf.split(self.sequences):
                        # Define training features and lengths
                        self.X, self.lengths = combine_sequences(train_index, self.sequences)
                        # Define testing features and lengths
                        X_test, lengths_test = combine_sequences(test_index, self.sequences)
                        # Fit model on training data
                        model = self.base_model(num_states)
                        # Calculate score on test data
                        logL = model.score(X_test, lengths_test)
                else:
                    # Fit model on available data and calculate score
                    model = self.base_model(num_states)
                    logL = model.score(self.X, self.lengths)

                # Update logLs
                logLs.append(logL)

                # Find mean of logLs and update models
                means.append(np.mean(logLs))
                models.append(model)
            except:
                pass

        # Check if there are means to find maximum for 
        if means:
            best_idx = means.index(max(means))
            return models[best_idx]
        else:
            return None
