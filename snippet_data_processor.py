# import timeit
from sys import getsizeof
import time
import pickle
import json

dir = '/home/touqir/courses/cmput_692/misc/Nikon_Snippets_Integrated.json'

toSave_corpus = {}
toSave_metadata = {}
PATH_corpus_metadata = "snippet_metadata.pickle"
PATH_corpus = "snippet_dictionary.pickle"
PATH_inverted_index = "snippet_invertedIndex.pickle"
PATH_postional_index = "snippet_positionalIndex.pickle"
snippet_id = 0 

def create_hash():

	global snippet_id, toSave_metadata
	toSave_metadata['IdToEntity'] = {}
	toSave_metadata['EntityToId'] = {}
	toSave_metadata['largestId'] = snippet_id
	f = open(dir, 'r')
	data = json.load(f)
	f.close()
	for k,v in data.items():
		parse(k, v)
	
	with open(PATH_corpus, 'wb') as f:
		pickle.dump(toSave_corpus, f)

	with open(PATH_corpus_metadata, 'wb') as f:
		pickle.dump(toSave_metadata, f)


def parse(key, value):

	global snippet_id
	snippet_ids = []
	for result in value:
		snippet = result['snippet']
		snippet = snippet.replace('\n', '')
		snippet = snippet.replace('\xa0...', ' . ')
		title = result['title']
		title = title.replace('.','')
		snippet += title
		snippet_id += 1
		toSave_corpus[snippet_id] = snippet.lower()
		snippet_ids.append(snippet_id)
		toSave_metadata['IdToEntity'][snippet_id] = key

	toSave_metadata['EntityToId'][key] = snippet_ids	
	toSave_metadata['largestId'] = snippet_id


def count_index():
	myIndex=set()
	with open(PATH_corpus, 'rb') as f:
		d=pickle.load(f)
		for v in d.values():
			splitted=v.split()
			for term in splitted:
				myIndex.add(term)

	print("length of index : ", len(myIndex))
	print("size of index: ", getsizeof(myIndex))


def create_index():
	with open(PATH_corpus, 'rb') as f:
		hash=pickle.load(f)
	t1 = time.time()
	create_invertedIndex(hash)
	create_positionalIndex(hash)
	print("time taken to create both indices : ", time.time() - t1)


def create_invertedIndex(hash):
	myIndex={}
	numbers=0
	for k,v in hash.items():
		# if numbers % 20000 == 0:
		# 	print(numbers)
		splitted=v.split()
		for term in splitted:
			# print(myIndex)
			if term not in myIndex:
				myIndex[term] = {}
				myIndex[term][k] = 1 
			else:
				if k in myIndex[term]:
					myIndex[term][k] += 1 				
				else:
					myIndex[term][k] = 1 

		numbers += 1

	with open(PATH_inverted_index, 'wb') as f:
		pickle.dump(myIndex, f)


def create_positionalIndex(hash):
	myIndex={}
	numbers=0
	for k,v in hash.items():
		# if numbers % 20000 == 0:
		# 	print(numbers)
		splitted=v.split()
		position = 0
		for term in splitted:
			# print(myIndex)
			if term not in myIndex:
				myIndex[term] = {}
				myIndex[term][k] = [position] 
			else:
				if k in myIndex[term]:
					myIndex[term][k].append(position) 				
				else:
					myIndex[term][k] = [position] 

			position += 1

		numbers += 1

	with open(PATH_postional_index, 'wb') as f:
		pickle.dump(myIndex, f)




if __name__=="__main__":
	create_hash()
	create_index()
