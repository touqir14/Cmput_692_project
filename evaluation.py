import algorithms
import random
import numpy as np
import pickle
import csv
import os

# DIR_location = 'kijiji+snippet'
DIR_location = 'kijiji'
PATH_test_cases = os.path.join("test_cases","test_case_3.pickle")
PATH_correlation_substring = os.path.join(DIR_location, "substring_correlations.pickle")
PATH_correlation_naive = os.path.join(DIR_location, "naive_correlations.pickle")
PATH_correlation_sequence = os.path.join(DIR_location, "sequence_correlations.pickle")
PATH_accuracy_data = os.path.join(DIR_location, "results", "accuracy_2.pickle")
PATH_results_csv = os.path.join(DIR_location, "results", "results_2.csv")
THRESHOLDS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

def run_evaluation_1():
	with open(PATH_test_cases, 'rb') as f:
		test_set = pickle.load(f)

	correlation_scores = {}
	if PATH_correlation_substring != "":
		with open(PATH_correlation_substring, 'rb') as f:
			correlation_scores['substring_match'] = pickle.load(f)

	if PATH_correlation_naive != "":
		with open(PATH_correlation_naive, 'rb') as f:
			correlation_scores['naive_match'] = pickle.load(f)

	if PATH_correlation_sequence != "":
		with open(PATH_correlation_sequence, 'rb') as f:
			correlation_scores['sequence_match'] = pickle.load(f)

	relevant_ads_dict = create_relevant_retrieved_ads_dictionaries(true_labels = test_set, predicted_labels = None)[0]
	predictions = predict_ads(THRESHOLDS, test_set, correlation_scores, ['substring_match', 'naive_match', 'sequence_match'])
	accuracy_data = {}

	for threshold, prediction_dict in predictions.items():

		accuracy_data[threshold] = {} 
		predicted_labels = prediction_dict['substring_match'].values()
		retrieved_ads_dict = create_relevant_retrieved_ads_dictionaries(true_labels = None, predicted_labels = predicted_labels)[1]
		avg_recall, avg_precision = calculate_recall_precision(relevant_ads_dict, retrieved_ads_dict)
		accuracy_data[threshold]['substring_match'] = {'precision' : avg_precision, 'recall' : avg_recall} 

		predicted_labels = prediction_dict['naive_match'].values()
		retrieved_ads_dict = create_relevant_retrieved_ads_dictionaries(true_labels = None, predicted_labels = predicted_labels)[1]
		avg_recall, avg_precision = calculate_recall_precision(relevant_ads_dict, retrieved_ads_dict)
		accuracy_data[threshold]['naive_match'] = {'precision' : avg_precision, 'recall' : avg_recall} 

		predicted_labels = prediction_dict['sequence_match'].values()
		retrieved_ads_dict = create_relevant_retrieved_ads_dictionaries(true_labels = None, predicted_labels = predicted_labels)[1]
		avg_recall, avg_precision = calculate_recall_precision(relevant_ads_dict, retrieved_ads_dict)
		accuracy_data[threshold]['sequence_match'] = {'precision' : avg_precision, 'recall' : avg_recall}


	with open(PATH_accuracy_data, 'wb') as f:
		pickle.dump(accuracy_data, f)

	export_results_csv(PATH_results_csv, accuracy_data)
	return accuracy_data


def export_results_csv(save_path, accuracy_data = None, fileName = None):

	firstRow = None
	allRows = []
	if accuracy_data == None:
		with open(fileName, 'rb') as f:
			accuracy_data = pickle.load(f)

	for threshold in THRESHOLDS:
		accuracy = accuracy_data[threshold]
		row = []
		if firstRow == None:
			firstRow = ['threshold']
			if 'substring_match' in accuracy: firstRow += ['substring_match_precision', 'substring_match_recall'] 
			if 'sequence_match' in accuracy: firstRow += ['sequence_match_precision', 'sequence_match_recall'] 
			if 'naive_match' in accuracy: firstRow += ['naive_match_precision', 'naive_match_recall'] 
			allRows.append(firstRow)

		row.append(threshold)
		if 'substring_match' in accuracy: row += [accuracy['substring_match']['precision'], accuracy['substring_match']['recall']] 
		if 'sequence_match' in accuracy: row += [accuracy['sequence_match']['precision'], accuracy['sequence_match']['recall']]
		if 'naive_match' in accuracy: row += [accuracy['naive_match']['precision'], accuracy['naive_match']['recall']]
		allRows.append(row)

	with open(save_path, 'w') as f:
		wr = csv.writer(f, quoting=csv.QUOTE_ALL)
		wr.writerows(allRows)

	return


def predict_ads(threshold_values, test_set, correlation, params):

	if 'substring_match' in params:
		substring_match = True
		substring_dict = {}
		substring_dict['largest_match'] = 0
		substring_dict['entityBySizeMatch'] = {}
		predictions_substring = {}
		substring_correlation_tokenSets = correlation['substring_match']["tokenSets"]
		entities = set(correlation['substring_match']['tokens'].keys())
	else:
		substring_match = False

	if 'naive_match' in params:
		naive_match = True
		naive_dict = {}
		naive_dict['largest_match'] = 0
		naive_dict['entityBySizeMatch'] = {}
		predictions_naive = {}
		naive_correlation_tokenSets = correlation['naive_match']['tokenSets']
		entities = set(correlation['naive_match']['tokens'].keys())
	else:
		naive_match = False

	if 'sequence_match' in params:
		sequence_match = True
		sequence_dict = {}
		sequence_dict['largest_match'] = 0
		sequence_dict['entityBySizeMatch'] = {}
		predictions_sequence = {}
		sequence_correlation_tokenSets = correlation['sequence_match']['tokenSets']
		entities = set(correlation['sequence_match']['tokens'].keys())
	else:
		sequence_match = False

	predictions = {}

	for threshold in threshold_values:
		predictions[threshold] = {}
		print('Working on threshold : ', threshold)
		for instance in test_set:
			ad = instance[1].lower()
			adID = instance[0]
			for entity in entities:
				
				if substring_match:
					tokenSet = substring_correlation_tokenSets[entity]
					substring_matches = find_substring_match(ad, tokenSet, entity, threshold)
					match_size = len(substring_matches[0])
					if match_size > substring_dict['largest_match']:
						substring_dict['largest_match'] = match_size
					if match_size not in substring_dict['entityBySizeMatch']:
						substring_dict['entityBySizeMatch'][match_size] = []
					substring_dict['entityBySizeMatch'][match_size].append(substring_matches)
				
				if naive_match:
					tokenSet = naive_correlation_tokenSets[entity]
					naive_matches = find_naive_match(ad, tokenSet, entity, threshold)
					match_size = len(naive_matches[0])
					if match_size > naive_dict['largest_match']:
						naive_dict['largest_match'] = match_size
					if match_size not in naive_dict['entityBySizeMatch']:
						naive_dict['entityBySizeMatch'][match_size] = []
					naive_dict['entityBySizeMatch'][match_size].append(naive_matches)
				
				if sequence_match:
					tokenSet = sequence_correlation_tokenSets[entity]
					sequence_matches = find_sequence_match(ad, tokenSet, entity, threshold)
					match_size = len(sequence_matches[0])
					if match_size > sequence_dict['largest_match']:
						sequence_dict['largest_match'] = match_size
					if match_size not in sequence_dict['entityBySizeMatch']:
						sequence_dict['entityBySizeMatch'][match_size] = []
					sequence_dict['entityBySizeMatch'][match_size].append(sequence_matches)


			if substring_match:
				max_size = substring_dict['largest_match']
				labelled_entity = max_aggregated_score_entity(substring_dict['entityBySizeMatch'][max_size])
				predictions_substring[adID] = [adID, ad, labelled_entity]
				substring_dict['largest_match'] = 0
				substring_dict['entityBySizeMatch'] = {}


			if naive_match:
				max_size = naive_dict['largest_match']
				labelled_entity = max_aggregated_score_entity(naive_dict['entityBySizeMatch'][max_size])
				predictions_naive[adID] = [adID, ad, labelled_entity]
				naive_dict['largest_match'] = 0
				naive_dict['entityBySizeMatch'] = {}


			if sequence_match:
				max_size = sequence_dict['largest_match']
				labelled_entity = max_aggregated_score_entity(sequence_dict['entityBySizeMatch'][max_size])
				predictions_sequence[adID] = [adID, ad, labelled_entity]
				sequence_dict['largest_match'] = 0
				sequence_dict['entityBySizeMatch'] = {}

		if substring_match:
			predictions[threshold]["substring_match"] = predictions_substring
			predictions_substring = {}

		if naive_match:	
			predictions[threshold]["naive_match"] = predictions_naive
			predictions_naive = {}

		if sequence_match:
			predictions[threshold]["sequence_match"] = predictions_sequence
			predictions_sequence = {}

	return predictions



def max_aggregated_score_entity(score_list):

	score_dict = {}
	for entity_struct in score_list:
		if entity_struct[0] == []:
			continue
		sum_score = sum(entity_struct[2])
		if sum_score not in score_dict:
			score_dict[sum_score] = []
		score_dict[sum_score].append(entity_struct)

	if score_dict != {}:
		max_score = max(score_dict.keys())
		max_scored_entity = random.choice(score_dict[max_score])[0][0]
	else:
		max_scored_entity = 'NO MATCH'

	return max_scored_entity


def create_relevant_retrieved_ads_dictionaries(true_labels=None, predicted_labels=None):
	relevant_ads_dict = None
	retrieved_ads_dict = None

	if true_labels != None:
		relevant_ads_dict = {}
		for instance in true_labels:
			if instance[2] not in relevant_ads_dict:
				relevant_ads_dict[instance[2]] = set()
			relevant_ads_dict[instance[2]].add(instance[0])

	if predicted_labels != None:
		retrieved_ads_dict = {}
		for instance in predicted_labels:
			if instance[2] not in retrieved_ads_dict:
				retrieved_ads_dict[instance[2]] = set()
			retrieved_ads_dict[instance[2]].add(instance[0])

	return [relevant_ads_dict, retrieved_ads_dict]



def find_substring_match(ad, tokenSets, entity, threshold):
	ad_tokens = algorithms.generate_tokenSet(ad, False)
	result = [[],[],[]]
	for tokens, score in tokenSets:
		if threshold != None:
			if score == None:
				continue
			if score < threshold:
				continue

		diff = None
		match_found = True
		ad_token_ptr = 0
		token_ptr = 0
		# print("length of ad_tokens: ", len(ad_tokens), ".. length of tokens: ", len(tokens))
		while True:
			# print(ad_token_ptr, token_ptr)
			if ad_tokens[ad_token_ptr] == tokens[token_ptr]:
				if diff == None:
					diff = ad_token_ptr - token_ptr
				ad_token_ptr += 1
				token_ptr += 1
			else:
				ad_token_ptr += 1

			if diff != None:
				if (ad_token_ptr - token_ptr) != diff:
					match_found = False
					break

			if (token_ptr == len(tokens)):
				break

			if ad_token_ptr >= len(ad_tokens):
				if token_ptr < len(tokens):
					match_found = False
				break

		if diff == None:
			match_found = False

		if match_found == True:
			result[0].append(entity)
			result[1].append(tokens)
			result[2].append(score)

	return result


def find_sequence_match(ad, tokenSets, entity, threshold):

	ad_tokens = algorithms.generate_tokenSet(ad, False)
	result = [[],[],[]]
	for tokens, score in tokenSets:
		if threshold != None:
			if score == None:
				continue
			if score < threshold:
				continue

		match_found = True
		ad_token_ptr = 0
		token_ptr = 0
		# print("length of ad_tokens: ", len(ad_tokens), ".. length of tokens: ", len(tokens))
		while True:
			# print(ad_token_ptr, token_ptr)
			if ad_tokens[ad_token_ptr] == tokens[token_ptr]:
				ad_token_ptr += 1
				token_ptr += 1
			else:
				ad_token_ptr += 1

			if (token_ptr == len(tokens)):
				break

			if ad_token_ptr >= len(ad_tokens):
				if token_ptr < len(tokens):
					match_found = False
				break

		if match_found == True:
			result[0].append(entity)
			result[1].append(tokens)
			result[2].append(score)

	return result


def find_naive_match(ad, tokenSets, entity, threshold):

	ad_tokens = algorithms.generate_tokenSet(ad, False)
	result = [[],[],[]]
	for tokens, score in tokenSets:
		if threshold != None:
			if score == None:
				continue
			if score < threshold:
				continue

		number_of_matches = 0
		for ad_token in ad_tokens:
			if ad_token in tokens:
				number_of_matches += 1

		if number_of_matches >= len(tokens):
			result[0].append(entity)
			result[1].append(tokens)
			result[2].append(score)

	return result


def calculate_recall_precision(relevant_ads_dict, retrieved_ads_dict):
	recalls = []
	precisions = []

	union_entities = set(relevant_ads_dict.keys()).union( retrieved_ads_dict.keys() )

	for entity in union_entities:

		if entity in relevant_ads_dict:
			relevant_ads = relevant_ads_dict[entity]
			relevant_ads_size = len(relevant_ads)
			calculate_recall = True

		else:
			relevant_ads = set()
			relevant_ads_size = 0
			calculate_recall = False

	
		if entity in retrieved_ads_dict:
			retrieved_ads = retrieved_ads_dict[entity]
			retrieved_ads_size = len(retrieved_ads)
			calculate_precision = True

		else:
			retrieved_ads = set()
			retrieved_ads_size = 0
			calculate_precision = False

		retrieved_relevant_intersection_size = len(retrieved_ads.intersection(relevant_ads))

		if calculate_recall is True:
			recall = retrieved_relevant_intersection_size / len(relevant_ads)
			recalls.append(recall)

		if calculate_precision is True:
			precision = retrieved_relevant_intersection_size / len(retrieved_ads)
			precisions.append(precision)

	avg_recall = 0
	avg_precision = 0

	if recalls != []:
		avg_recall = np.mean(recalls)

	if precisions != []:
		avg_precision = np.mean(precisions)

	return [avg_recall, avg_precision]


if __name__ == "__main__":

	run_evaluation_1()