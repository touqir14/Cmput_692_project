from googleapiclient.discovery import build
import csv
import json
import pprint
import pickle

my_api_key = "AIzaSyD7TmlJcZ_LZwTmEAj_Y_mnd85SnmdO44Q"
my_cse_id = "008695887468451610222:jbf4rpx3qsq"

def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']

dict={}




with open('../Nikon_Entities_Remaining.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, dialect=csv.excel_tab)
        for row in reader:
            dict[row[0]] = google_search(row[0], my_api_key, my_cse_id, num=10)
            with open('Nikon_snippets.json', 'wb') as f:
                json.dump(dict, f, indent=2)

