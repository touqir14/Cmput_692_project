# import timeit
from sys import getsizeof
import time
import json
from sys import getsizeof
import collections
import pickle
# import timeit
from sys import getsizeof
import time
import csv
import io
output = io.StringIO()

dir = '/Users/sasa/Dropbox/1-Uni/CMPUT 692/Project/Code/google_snippet/Nikon_Snippets_Integrated.json'

import pickle



def create_pickle_from_json():
    f = open(dir, 'r')
    jsonvalues = json.load(f)
    f.close()
    with open('/Users/sasa/Dropbox/1-Uni/CMPUT 692/Project/Code/Nikon_Entities.csv', 'rU') as csvfile:
        reader = csv.reader(csvfile, dialect=csv.excel_tab)
        i=0
        ParentIndex = {}
        for row in reader:
            i = i + 1
            #if (i > 1):
            #    break
            print(row[0])
            k = row[0]
            myIndex = {}
            for criteria in jsonvalues[row[0]]:


                splitted = str(criteria['title']).lower().split()

                for term in splitted:
                    if ((term not in str(k).lower()) and (term not in ["...", "|",":",",","at","from","to","for",'/',"with","and","or", "the","b&h", '_','-', '&',"review:", "reviews", "review", "w/","w/o", "amazon.com","youtube"])):
                        #print(term)
                        term = term.replace("(", "")
                        term = term.replace(")", "")
                        term = term.replace("{", "")
                        term = term.replace("}", "")
                        term = term.replace("!", "")
                        term = term.replace(":", "")
                        term = term.replace("|", "")

                        if term not in myIndex:
                            myIndex[term] = {}
                            myIndex[term] = 1
                        else:
                            if term in myIndex:
                                myIndex[term] += 1
                        #print(myIndex)

            ParentIndex[str(k).lower()]=myIndex
            print(k)
            print(ParentIndex[str(k).lower()])
        with open('/Users/sasa/Dropbox/1-Uni/CMPUT 692/Project/Code/dictionary_Nikon_Snippet_Surroundings.pickle', 'wb') as fsurr:
            pickle.dump(ParentIndex, fsurr)


if __name__ == "__main__":

    create_pickle_from_json()