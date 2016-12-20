from sys import getsizeof
import collections
import pickle
# import timeit
from sys import getsizeof
import time
import csv
import io
output = io.StringIO()


with open('/Users/sasa/Dropbox/1-Uni/CMPUT 692/Project/Code/dictionary.pickle', 'rb') as f2:
    d2=pickle.load(f2)
    with open('/Users/sasa/Dropbox/1-Uni/CMPUT 692/Project/Code/invertedindex.pickle', 'rb') as f:
        d = (pickle.load(f))
        Container={}
        Brand='nikon'
        Container= (d[Brand])
        excelsheet=[]
        with open('/Users/sasa/Dropbox/1-Uni/CMPUT 692/Project/Code/movie_Ads.csv', 'w') as csvfile2:
            writer = csv.writer(csvfile2)
            for value in Container:
                excelrow = []
                excelrow.append(value)
                excelrow.append(Container[value])
                excelrow.append(d2[value])
                excelsheet.append(excelrow)
                writer.writerow((excelrow))











