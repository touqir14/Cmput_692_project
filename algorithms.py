import pickle
import itertools
import numpy
import copy
import math
import shutil
import kijiji_settings as default_settings
import builtins
import os


# ad_dictionary = None
# invertedIndex = None

def loadFiles(params):
	# global ad_dictionary, invertedIndex

	return_values = []
	if "corpus" in params:
		with open(SETTINGS.PATH_dictionary, 'rb') as f:
			ad_dictionary = pickle.load(f)
			return_values.append(ad_dictionary)

	if "inv_index" in params:
		with open(SETTINGS.PATH_invertedIndex, 'rb') as f:
			invertedIndex = pickle.load(f)
			return_values.append(invertedIndex)

	if "pos_index" in params:
		with open(SETTINGS.PATH_positionalIndex, 'rb') as f:
			positionalIndex = pickle.load(f)
			return_values.append(positionalIndex)

	return return_values


def save_IDF(corpus_size, invertedIndex, tokenSet_location, save_location):
	tokenSet = None
	dictionary = None
	with open(tokenSet_location, 'rb') as f:
		dictionary = pickle.load(f)
		tokenSet = dictionary['tokens']

	entities = list(tokenSet.keys())

	for entity in entities:
		tokens = tokenSet[entity]
		for token in tokens:
			documents = invertedIndex.get(token)
			if documents != None:
				idf = math.log(corpus_size / len(documents.keys()) ) 
			else:
				idf = 0
			tokens[tokens.index(token)] = [token, idf]

	with open(save_location, 'wb') as f:
		pickle.dump(dictionary, f)


def generate_tokenSet(entity, willgenerate_tokenSet=True):
	tokenSet = []
	tokens = entity.split(" ")
	comma_seperated_tokens = []
	tokens_clone = copy.deepcopy(tokens)
	for token in tokens:
		splitted = token.split(',')
		splitted_clone = copy.deepcopy(splitted)
		if len(splitted) > 1:
			for entry in splitted:
				if (entry.strip() == '') or (entry.strip() == ','):
					splitted_clone.remove(entry)  
			ind = tokens_clone.index(token)
			# print(splitted_clone)
			tokens_clone = tokens_clone[0:ind] + splitted_clone + tokens_clone[ind+1:]

	if willgenerate_tokenSet == True:
		for length in range(1, len(tokens_clone) + 1): 
			for subset in itertools.combinations(tokens_clone, length):
				tokenSet.append(subset)

		return tokenSet, tokens_clone
	
	else:
		return tokens_clone


def save_tokenSets(entity_location, save_location):
	entities = None
	with open(entity_location, 'rb') as f:
		entities = pickle.load(f)

	tokenSets_dictionary = {}
	token_dictionary = {}
	for entity in entities:
		original_entity = copy.deepcopy(entity)
		entity = entity.lower()
		tokenSet, tokens = generate_tokenSet(entity)
		tokenSets_dictionary[original_entity] = tokenSet
		token_dictionary[original_entity] = tokens 

	with open(save_location, 'wb') as f:
		toSave = {}
		toSave['tokenSets'] = tokenSets_dictionary
		toSave['tokens'] = token_dictionary
		pickle.dump(toSave, f)



def calculate_relaxed_evidence(type, tokenSet_location, save_location, ad_dictionary, invertedIndex=None, positionalIndex=None):
	if type not in ["substring_match", "sequence_match", "naive_match"]:
		print('Error! Please pass the correct "type" parameter!')
		return

	tokenSet = None
	entitySet = None
	with open(tokenSet_location, 'rb') as f:
		dictionary = pickle.load(f)
		tokenSet = dictionary['tokenSets']
		entitySet = dictionary['tokens']

	entities = list(tokenSet.keys())

#######################################################################
	if type == "substring_match":
		if positionalIndex == None:
			print("please pass a positional Index!")
			return

		print("performing substring_match based correlation calculation")
		i = 0
		for entity in entities:
			i += 1
			print("processing entity : ", i)
			tokensets = tokenSet[entity]
			tokensets_clone = copy.deepcopy(tokensets)
			for tokens in tokensets:
				intersection = set()
				empty_intersection = True
				correlations = []
				willSkip = False
				for token in tokens:
					documents = positionalIndex.get(token)
					if documents != None:
						if empty_intersection == True:
							intersection = set(documents.keys())
							empty_intersection = False
						else:
							intersection.intersection_update( set(documents.keys()) )

					else:
						# If a token is not in the index, we choose the next tokenset
						willSkip = True
						break
				
				if willSkip == False:
					for docID in intersection:
						CurrentPos = None
						tokenCount = 0
						for token in tokens:
							documents = positionalIndex.get(token)
							if documents != None:
								# We will use the term's first occurance position if there are multiple occurances.
								positions = documents[docID]
								if CurrentPos == None:
									CurrentPos = positions[0]
									tokenCount += 1
								else:
									termFound_nextPosition = False
									for position in positions:
										if position == (CurrentPos + 1):
											CurrentPos += 1
											tokenCount += 1
											termFound_nextPosition = True
											break

									if termFound_nextPosition == False:
										# if we see that the next token is not the immediately right to the previous token, we break the loop and go to the next document
										break

							else:
								willSkip = True
								break

						if willSkip == True:
							break

						if tokenCount == len(tokens):
							doc = ad_dictionary[docID]
							correlations.append( calculate_correlation(doc, entity, entitySet) )

				mean_correlation = None
				if (willSkip == False) and (len(correlations) != 0):
					mean_correlation = numpy.mean(correlations)
				tokensets_clone.remove(tokens)
				tokensets_clone.append([tokens, mean_correlation])
			
			tokenSet[entity] = tokensets_clone
		
		with open(save_location, 'wb') as f:
			dictionary['type'] = "substring_match"
			pickle.dump(dictionary, f)

###################################################################
	if type == "sequence_match":
		if positionalIndex == None:
			print("please pass a positional Index!")
			return

		print("performing sequence_match based correlation calculation")
		i = 0
		for entity in entities:
			i += 1
			print("processing entity : ", i)
			tokensets = tokenSet[entity]
			tokensets_clone = copy.deepcopy(tokensets)
			for tokens in tokensets:
				intersection = set()
				empty_intersection = True
				correlations = []
				willSkip = False
				for token in tokens:
					documents = positionalIndex.get(token)
					if documents != None:
						if empty_intersection == True:
							intersection = set(documents.keys())
							empty_intersection = False
						else:
							intersection.intersection_update( set(documents.keys()) )

					else:
						# If a token is not the index, we choose the next tokenset
						willSkip = True
						break
				
				if willSkip == False:
					for docID in intersection:
						CurrentPos = None
						tokenCount = 0
						for token in tokens:
							documents = positionalIndex.get(token)
							if documents != None:
								# We will use the term's first occurance position if there are multiple occurances.
								positions = documents[docID]
								if CurrentPos == None:
									CurrentPos = positions[0]
									tokenCount += 1
								else:
									termFound_nextPosition = False
									for position in positions:
										if position > CurrentPos:
											CurrentPos = position
											tokenCount += 1
											termFound_nextPosition = True
											break

									if termFound_nextPosition == False:
										# if we see that the tokens in the ads are not in sequence as in the tokenset, we break the loop and go to the next document
										break

							else:
								willSkip = True
								break

						if willSkip == True:
							break

						if tokenCount == len(tokens):
							doc = ad_dictionary[docID]
							correlations.append( calculate_correlation(doc, entity, entitySet) )

				mean_correlation = None
				if (willSkip == False) and (len(correlations) != 0):
					mean_correlation = numpy.mean(correlations)
				tokensets_clone.remove(tokens)
				tokensets_clone.append([tokens, mean_correlation])
			
			tokenSet[entity] = tokensets_clone
		
		with open(save_location, 'wb') as f:
			dictionary['type'] = "sequence_match"
			pickle.dump(dictionary, f)

###################################################################

	if type == "naive_match":
		Index = None
		if (invertedIndex == None) and (positionalIndex == None):
			print("please pass an inverted Index!")
			return
		
		print("performing sequence_match based correlation calculation")

		if positionalIndex != None:
			Index = positionalIndex

		if invertedIndex != None:
			Index = invertedIndex

		i = 0
		for entity in entities:
			i += 1
			print("processing entity : ", i)
			tokensets = tokenSet[entity]
			tokensets_clone = copy.deepcopy(tokensets)
			for tokens in tokensets:
				intersection = set()
				empty_intersection = True
				correlations = []
				willSkip = False
				for token in tokens:
					documents = Index.get(token)
					if documents != None:
						if empty_intersection == True:
							intersection = set(documents.keys())
							empty_intersection = False
						else:
							intersection.intersection_update( set(documents.keys()) )

					else:
						# If a token is not the index, we choose the next tokenset
						willSkip = True
						break
				
				if willSkip == False:
					for docID in intersection:
						doc = ad_dictionary[docID]
						correlations.append( calculate_correlation(doc, entity, entitySet) )

				mean_correlation = None
				if (willSkip == False) and (len(correlations) != 0):
					mean_correlation = numpy.mean(correlations)
				tokensets_clone.remove(tokens)
				tokensets_clone.append([tokens, mean_correlation])
			
			tokenSet[entity] = tokensets_clone
		
		with open(save_location, 'wb') as f:
			dictionary['type'] = "naive_match"
			pickle.dump(dictionary, f)

	return


def calculate_correlation(doc, entity, entitySet):
	doc_terms = set( generate_tokenSet(doc, willgenerate_tokenSet = False) )
	entityTokens = set()
	score_normalizer = 0
	for token, idf in entitySet[entity]:
		entityTokens.add(token)
		score_normalizer += idf

	tokens_found = entityTokens.intersection(doc_terms)
	score_unnormalized = 0
	for token, idf in entitySet[entity]:
		if token in tokens_found:
			score_unnormalized += idf

	normalized_document_score = score_unnormalized / score_normalizer
	return normalized_document_score


def generate_correlationScores():

	if SETTINGS.DIR_toSave != '':
		if not os.path.isdir(SETTINGS.DIR_toSave):
			os.mkdir(SETTINGS.DIR_toSave)


	if SETTINGS.EXACT_EVIDENCE == True:
		pass

	if SETTINGS.RELAXED_EVIDENCE == True:

		[ad_dictionary, positionalIndex] = loadFiles(['corpus','pos_index'])

		if SETTINGS.PATH_substring_correlation != None:

			# print("Calculating substring_match based correlation")
			save_location = os.path.join(SETTINGS.DIR_toSave, SETTINGS.PATH_substring_correlation)
			tokenSet_location = SETTINGS.PATH_IDF
			calculate_relaxed_evidence("substring_match", tokenSet_location, save_location, ad_dictionary, positionalIndex=positionalIndex)

		if SETTINGS.PATH_sequence_correlation != None:

			# print("Calculating sequence_match based correlation")
			save_location = os.path.join(SETTINGS.DIR_toSave, SETTINGS.PATH_sequence_correlation)
			tokenSet_location = SETTINGS.PATH_IDF
			calculate_relaxed_evidence("sequence_match", tokenSet_location, save_location, ad_dictionary, positionalIndex=positionalIndex)

		if SETTINGS.PATH_naive_correlatation != None:

			# print("Calculating naive_match based correlation")
			save_location = os.path.join(SETTINGS.DIR_toSave, SETTINGS.PATH_naive_correlatation)
			tokenSet_location = SETTINGS.PATH_IDF
			calculate_relaxed_evidence("naive_match", tokenSet_location, save_location, ad_dictionary, positionalIndex=positionalIndex)

	return


def generate_IDF():
	[ad_dictionary, invertedIndex] = loadFiles(['corpus','inv_index'])
	corpus_size = len(ad_dictionary.keys())
	save_IDF(corpus_size, invertedIndex, tokenSet_location = SETTINGS.PATH_TokenSet, save_location = SETTINGS.PATH_IDF)
	return


if __name__ == "__main__":
	builtins.SETTINGS = default_settings


	# entity_location = "entities.pickle"
	# tokenSet_location = "tokenSets.pickle"
	# save_tokenSets(entity_location, tokenSet_location)
	# save_IDF_location = "idf_values.pickle"
	# [ad_dictionary, invertedIndex] = loadFiles(['corpus','inv_index'])
	# corpus_size = len(ad_dictionary.keys())
	# save_IDF(corpus_size, invertedIndex, tokenSet_location, save_IDF_location)


	# [ad_dictionary, positionalIndex] = loadFiles(['corpus','pos_index'])
	# tokenSet_location = "idf_values.pickle"
	# save_location = "correlation_scores.pickle"
	# calculate_relaxed_evidence("substring_match", tokenSet_location, save_location, ad_dictionary, positionalIndex=positionalIndex)


	generate_correlationScores()
# def calculate_relaxed_evidence(type, tokenSet_location, save_location, ad_dictionary, invertedIndex=None, positionalIndex=None):
