# import timeit
from sys import getsizeof
import time
import pickle
import json
import os


PATH_snippet_corpus = os.path.join("snippets", "snippet_dictionary.pickle")
PATH_kijiji_corpus = os.path.join("kijiji", "kijiji_dictionary.pickle")
PATH_kijiji_snippet_corpus = os.path.join("kijiji+snippet", "kijiji+snippet_dictionary.pickle")
PATH_inverted_index = os.path.join("kijiji+snippet", "kijiji+snippet_invertedIndex.pickle")
PATH_postional_index = os.path.join("kijiji+snippet", "kijiji+snippet_positionalIndex.pickle")


def merge_dictionaries():

	kijiji_dictionary = None
	snippets_dictionary = None

	with open(PATH_snippet_corpus, 'rb') as f:
		snippets_dictionary = pickle.load(f)

	with open(PATH_kijiji_corpus, 'rb') as f:
		kijiji_dictionary = pickle.load(f)

	kijiji_dictionary.update(snippets_dictionary)

	with open(PATH_kijiji_snippet_corpus, 'wb') as f:
		pickle.dump(kijiji_dictionary, f)



def count_index():
	myIndex=set()
	with open(PATH_kijiji_snippet_corpus, 'rb') as f:
		d=pickle.load(f)
		for v in d.values():
			splitted=v.split()
			for term in splitted:
				myIndex.add(term)

	print("length of index : ", len(myIndex))
	print("size of index: ", getsizeof(myIndex))


def create_index():
	with open(PATH_kijiji_snippet_corpus, 'rb') as f:
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
	merge_dictionaries()
	create_index()
