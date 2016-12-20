import os

DIR_toSave = "snippets" # If in the same folder then have this variable as an empty string
PATH_dictionary = os.path.join(DIR_toSave, "snippet_dictionary.pickle")
PATH_invertedIndex = os.path.join(DIR_toSave, "snippet_invertedIndex.pickle")
PATH_positionalIndex = os.path.join(DIR_toSave, "snippet_positionalIndex.pickle")
PATH_IDF = os.path.join(DIR_toSave, "idf_values.pickle")
PATH_TokenSet = "tokenSets.pickle"

PATH_substring_correlation = "substring_correlations.pickle"
PATH_sequence_correlation = "sequence_correlations.pickle"
PATH_naive_correlatation = "naive_correlations.pickle"


RELAXED_EVIDENCE = True
EXACT_EVIDENCE = True