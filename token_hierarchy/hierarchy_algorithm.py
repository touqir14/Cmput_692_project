import pickle
import os

PATH_tokenSet = "../tokenSets.pickle"
PATH_invertedIndex = os.path.join('../','kijiji','kijiji_invertedIndex.pickle')
PATH_token_hierarchy = "token_hierarchy.pickle"

def find_hierarchy(entity_tokens, invertedIndex):

	intersection_scores = {}
	relevance_score = []
	hierarchicaly_sorted_dict = {}
	inverse_hierarchy_index = {}
	i = 0
	for entity, tokens in entity_tokens.items():
		print ("processing entity : ", i)
		i += 1
		scores = []
		for token1 in tokens:
			docs1 = invertedIndex.get(token1)
			token1_score = 0
			if docs1 != None:
				docs1_ids = set(docs1.keys())
				for token2 in tokens:
					if token1 != token2:
						if (token1, token2) in intersection_scores:
							token1_score += intersection_scores[(token1, token2)]
						else:
							docs2 = invertedIndex.get(token2)
							if docs2 != None:
								docs2_ids = set(docs2.keys())
								token1_score += len(docs2_ids.intersection(docs1_ids)) / len(docs2_ids)
								intersection_scores[(token1, token2)] = token1_score

			scores.append([token1, token1_score])

		scores = sorted(scores, key = lambda x:x[1], reverse=True)
		hierarchicaly_sorted = []
		for token, score in scores:
			hierarchicaly_sorted.append(token)
		
		hierarchicaly_sorted = tuple(hierarchicaly_sorted)
		hierarchicaly_sorted_dict[entity] = hierarchicaly_sorted
		pos = 1
		for token in hierarchicaly_sorted:
			if token not in inverse_hierarchy_index:
				inverse_hierarchy_index[token] = []
			inverse_hierarchy_index[token].append([hierarchicaly_sorted, pos])
			pos += 1

	return hierarchicaly_sorted_dict, inverse_hierarchy_index


def create_token_hierarchy():

	with open(PATH_invertedIndex, 'rb') as f:
		invertedIndex = pickle.load(f)

	with open(PATH_tokenSet, 'rb') as f:
		tokenSet = pickle.load(f)

	hierarchicaly_sorted_dict, inverse_hierarchy_index = find_hierarchy(tokenSet['tokens'], invertedIndex)
	toSave = {}
	toSave['dict'] = hierarchicaly_sorted_dict
	toSave['index'] = inverse_hierarchy_index

	with open(PATH_token_hierarchy, 'wb') as f:
		pickle.dump(toSave, f)



if __name__ == "__main__":

	create_token_hierarchy()