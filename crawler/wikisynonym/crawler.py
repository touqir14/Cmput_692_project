import urllib
from bs4 import BeautifulSoup
from tornado import ioloop, httpclient
import csv
import pickle

entityTableFile = "Entity_list.csv"
synonymsFile = "wiki_synonyms"
url = "http://wikisynonyms.ipeirotis.com/search" #Url for the wikipedia synonyms page that we will crawl.
toFetch=0
synonyms={}
suggestions={}

def run():
    entities = loadInputEntities()
    crawl(entities)
    saveSynonyms()

    # print("printing synonyms")
    # print(synonyms)
    # print("printing suggestions")
    # print(suggestions)

def saveSynonyms():
    toSave = {"synonyms" : synonyms, "suggestions" : suggestions}
    with open(synonymsFile, 'wb') as f:
        pickle.dump(toSave, f)

def loadInputEntities():
    with open(entityTableFile,'r') as f:
        rows = list(csv.reader(f))

    entities=[]
    for row in rows[:-2]:
        entities.append(row[0].strip())

    return entities


def crawl(entities):
    global toFetch
    client = httpclient.AsyncHTTPClient()
    for entity in entities:
        toFetch += 1
        post = {"term" : entity}
        body = urllib.parse.urlencode(post)
        client.fetch(url, handle_request, method='POST', headers=None, body=body)
    ioloop.IOLoop.instance().start()


def handle_request(response):
    global toFetch, synonyms
    toFetch -= 1
    soup = BeautifulSoup(response.body, 'html.parser')

    entity=soup.select('input[id="term"]')[0].get('value')
    synonyms[entity] = "NOT-FOUND"

    if len(soup.select('div[class="alert alert-error"]')) == 0:
        results=soup.select('span[class="term"]')
        if len(results) != 0:
            synonyms[entity] = []
            for result in results:
                splitted=result.get_text().split('.')
                splitted[1] = splitted[1].strip()
                text=".".join(splitted[1:])
                synonyms[entity].append(text) 
        else:
            suggested_results = soup.select('a[class="search-again"]')
            if len(suggested_results) != 0:
                synonyms[entity] = "HAS-SUGGESTIONS"
                suggestions[entity] = []
                for result in suggested_results:
                    text=result.get_text().strip()
                    suggestions[entity].append(text)



    if toFetch == 0:
        ioloop.IOLoop.instance().stop()


if __name__ == "__main__":

    run()