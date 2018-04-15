import warnings
from asl_data import SinglesData

import operator

def recognize(models: dict, test_set: SinglesData):
    """ Recognize test word sequences from word models set

   :param models: dict of trained models
       {'SOMEWORD': GaussianHMM model object, 'SOMEOTHERWORD': GaussianHMM model object, ...}
   :param test_set: SinglesData object
   :return: (list, list)  as probabilities, guesses
       both lists are ordered by the test set word_id
       probabilities is a list of dictionaries where each key a word and value is Log Liklihood
           [{SOMEWORD': LogLvalue, 'SOMEOTHERWORD' LogLvalue, ... },
            {SOMEWORD': LogLvalue, 'SOMEOTHERWORD' LogLvalue, ... },
            ]
       guesses is a list of the best guess words ordered by the test set word_id
           ['WORDGUESS0', 'WORDGUESS1', 'WORDGUESS2',...]
   """
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    # Intialize probabilities and guesses lists
    probabilities = []
    guesses = []

    # Iterate through number of words
    for word_id in range(0, len(test_set.get_all_Xlengths())):
        # Define features and lengths
        X, lengths = test_set.get_item_Xlengths(word_id)
        # Initialize empty dictionary for word and logL
        d = {}
        # Iterate through word and model of models
        for word, model in models.items():
            try:
                # Caclculate logL
                logL = model.score(X, lengths)
                # Update dictionary
                d[word] = logL
            except:
                d[word] = float("-inf")
                pass

        # Updage probabilities list
        probabilities.append(d)

        # Check if there is a dictionary to find maximum logL
        if d:
            guess = max(d, key=d.get)
        else:
            guess = float("-inf")
        guesses.append(guess)

    # Return updated probabilities and guesses 
    return (probabilities, guesses)
