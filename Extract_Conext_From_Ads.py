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



def create_Context_pickle_from_CSV():
    #f = open(dir, 'r')
    #jsonvalues = json.load(f)
    #f.close()
    with open('/Users/sasa/Dropbox/1-Uni/CMPUT 692/Project/Code/Nikon_Ads.csv', 'rU') as csvfile:
        reader = csv.reader(csvfile, dialect=csv.excel_tab)
        i=0
        ParentIndex = {}
        for row in reader:
            i = i + 1
            #if (i > 1):
                #break
            print(row[0])
            k = row[0]
            myIndex = {}
            splitted = str(k).lower().split(",")
            print(str(i)+","+splitted[0]+","+splitted[2]+","+splitted[3])
            AdvWords=splitted[2].split()
            for term in (AdvWords):
                term = term.replace("(", "")
                term = term.replace(")", "")
                term = term.replace("{", "")
                term = term.replace("}", "")
                term = term.replace("!", "")
                term = term.replace(":", "")
                term = term.replace("|", "")
                if ((splitted[3]!="no match") and (term not in str(splitted[3]).lower()) and (term not in ["...", "|",":",",","at","from","to","for",'/',"with","and","or", "the","b&h", '_','-','+', '&',"wanted", "reviews", "review", "w/","w/o", "amazon.com","youtube"])):


                    if term not in myIndex:
                        myIndex[term] = {}
                        myIndex[term] = 1
                    else:
                        if term in myIndex:
                            myIndex[term] += 1
                        #print(myIndex)
            ParentIndex[splitted[0]]=myIndex
            print(ParentIndex[splitted[0]])
        with open('/Users/sasa/Dropbox/1-Uni/CMPUT 692/Project/Code/Nikon_Ads_Context.pickle', 'wb') as fsurr:
            pickle.dump(ParentIndex, fsurr)


if __name__ == "__main__":
    create_Context_pickle_from_CSV()
