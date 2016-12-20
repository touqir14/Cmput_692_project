import csv
import pickle

PATH_test_csv = 'ads.csv'
PATH_toSave = 'test_case_1.pickle'
PATH_tokenSets = '../tokenSets.pickle'

def process_raw_1(tokenSets):
	"""
	For this function, I assigned NO MATCH if there are multiple labels for an ad or the label is not present in my original entitySet
	"""
	tokens = tokenSets['tokens']
	with open(PATH_test_csv, 'r') as f:
		tests = list(csv.reader(f))

	toSave = []
	for test in tests:
		splitted = test[2].split('\n')
		if splitted[0] != '':
			if len(splitted) > 1:
				test[2] = 'NO MATCH'
			else:	
				if tokens.get(splitted[0]) == None:
					test[2] = 'NO MATCH'

			toSave.append(test)

	with open(PATH_toSave, 'wb') as f:
		pickle.dump(toSave, f)



def gen_test_case_1():
	tokenSets = None

	with open(PATH_tokenSets, 'rb') as f:
		tokenSets = pickle.load(f)

	process_raw_1(tokenSets)


if __name__ == "__main__":
	gen_test_case_1()




