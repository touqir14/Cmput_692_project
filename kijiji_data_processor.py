# import timeit
from sys import getsizeof
import time

dir = '/home/touqir/courses/cmput_692/Old_data.txt'

import pickle
toSave = {}
index = "invertedIndex"

def create_hash():

	f = open(dir, 'r')
	for line in f:
		parse(line)
	f.close()
	
	with open('dictionary.pickle', 'wb') as f:
		pickle.dump(toSave, f)


def parse(text):
	splitted=text.split('<KDTAB>')
	id = splitted[0]
	ad_title = splitted[2]
	# if index == "invertedIndex":
	toSave[int(id)] = ad_title.lower()


def count_index():
	myIndex=set()
	with open('dictionary.pickle', 'rb') as f:
		d=pickle.load(f)
		for v in d.values():
			splitted=v.split()
			for term in splitted:
				myIndex.add(term)

	print("length of index : ", len(myIndex))
	print("size of index: ", getsizeof(myIndex))


def create_index():
	with open('dictionary.pickle', 'rb') as f:
		hash=pickle.load(f)
	t1 = time.time()
	# create_invertedIndex(hash)
	create_positionalIndex(hash)
	print("time taken to create index : ", time.time() - t1)


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

	with open('invertedIndex.pickle', 'wb') as f:
		pickle.dump(myIndex, f)
	# print(myIndex)


def create_positionalIndex(hash):
	myIndex={}
	numbers=0
	for k,v in hash.items():
		if numbers % 20000 == 0:
			print(numbers)
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

	with open('positionalIndex.pickle', 'wb') as f:
		pickle.dump(myIndex, f)
	# print(myIndex)




if __name__=="__main__":
	# create_hash()
	# count_index()
	create_index()
	# test = {1:"i am there to help you i", 2:"am i to see you"}
	# create_invertedIndex(test)
	# create_positionalIndex(test)