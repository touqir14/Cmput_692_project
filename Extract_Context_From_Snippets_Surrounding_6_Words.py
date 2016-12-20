from sys import getsizeof
import collections
import pickle
# import timeit
from sys import getsizeof
import time
import csv
import io
output = io.StringIO()


with open('../dictionary_Nikon_Snippet_Surroundings.pickle', 'rb') as f:
    d = (pickle.load(f))
    with open('/Users/sasa/Dropbox/1-Uni/CMPUT 692/Project/Code/Nikon_Entities.csv', 'rU') as csvfile:
        reader = csv.reader(csvfile, dialect=csv.excel_tab)
        #with open('/Users/sasa/Dropbox/1-Uni/CMPUT 692/Project/Code/Nikon_context.csv', 'w') as csvfile2:
        with open('/Users/sasa/Dropbox/1-Uni/CMPUT 692/Project/Code/Nikon_context.pickle', 'wb') as picklefile:
            #writer = csv.writer(csvfile2)
            Nikon_Surr={}
            for row in reader:
                print(row[0])
                #excelrow=[row[0]]
                excelrow = []
                surr={}
                #print(d[row[0]])
                surr= collections.Counter(d[row[0].lower()])
                mc=(surr.most_common(6))
                #print(mc)
                for value in mc:
                    excelrow.append(value[0])
                Nikon_Surr[str(row[0]).lower()]=excelrow
                print(Nikon_Surr[str(row[0]).lower()])
            pickle.dump(Nikon_Surr, picklefile)
                #writer.writerow((excelrow))





