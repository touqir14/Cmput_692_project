import requests
# import scrapy
import re
import time
import datetime
import pickle
import threading
from threading import Timer
from tornado import ioloop, httpclient
import os.path
from bs4 import BeautifulSoup
# import _thread

# from parser import Parser
"""
This file consists of crawler class which is mainly responsible for crawling
webpages.

"""
PARAMS_DIR = "params.pickle"
ENTITY_LIST_DIR = "entityList.csv"
IDs_DIR = "IDs.pickle"

class Crawler():

    name="kijiji_standard"

    def __init__(self):
        # self.current_URL=input("Please enter the URL to start crawling from : ")
        # self.current_URL='http://www.kijiji.ca/b-buy-sell/edmonton/c10l1700203'
        # self.restartInterval = 60 # in munutes
        self.Parser=Parser(parser_type=1)
        self.pagesCrawled=0
        self.pagesCrawlMax=100
        self.eachPageSize=25
        self.linksCrawlMax = self.pagesCrawlMax * self.eachPageSize
        self.linksCrawled=[]
        self.entityListFileName=ENTITY_LIST_DIR
        self.allIds = set()
        self.data = {}
        self.metaData = {}
        self.paramsFileName = PARAMS_DIR
        self.IDsFileName = IDs_DIR
        self.lastSaveTime = time.time()
        self.lastCrawlTime = time.time()
        self.runsSoFar = 0
        self.crawling = False
        self.crawled = 0
        self.toExit = False
        self.no_linksToFetch = 0
        self.page_signatures = []

        self.http_client = httpclient.AsyncHTTPClient()

        self.loadALL()

        # print("self.toCrawlSize: ", self.toCrawlSize)


    def runLoop(self):

        # print("right here!!!!!!! 4: ", self.toCrawlSize," ", self.crawled)

        if self.crawled < self.toCrawlSize : 
            # print("right here!!!!!!! 4.1")

            if not self.crawling:
                # self.loadParams()
                self.restartRun()
                self.isToSave()
                self.lastCrawlTime = time.time()
                self.crawling = True

            self.current_URL = next(self.toCrawl)
            self.crawled += 1 
            self.http_client.fetch(self.current_URL.strip(), self.handle_request, method='GET')
            # print("right here!!!!!!! 5")

            ioloop.IOLoop.instance().start()
            self.no_linksToFetch = 0 # In case timeout occurs and linksRequested != 0
            self.pagesCrawled = 0
            # print("right here!!!!!!! 6")
            threading.Thread(target=self.runLoop).start()

        else:
    
            self.runsSoFar += 1
            print("self.runsSoFar: ", self.runsSoFar, " . RUN DURATION: ", time.time() - self.runDuration)
            self.isToSave()

            if self.runsSoFar < self.numberOfRuns : #Need to check whether the number of run sessions exceeded the maximum preset number of runs
                self.crawling = False
                self.crawled = 0
                toSleep = self.lastCrawlTime + self.crawlPeriod - time.time()
                self.thread=Timer(toSleep, self.runLoop)
                self.thread.start()



    # def crawl_parse(self, response):
    #     print("crawled URL: ", response.effective_url)
    #     print("self.lastSaveTime: ", self.lastSaveTime)
    #     print("self.lastCrawlTime: ", self.lastCrawlTime)
    #     # print("self.runsSoFar: ", self.runsSoFar)
    #     print("self.crawling : ", self.crawling)
    #     print("self.crawled : ", self.crawled)

    #     ioloop.IOLoop.instance().stop()


    def createSignatures(self):

        if self.page_signatures == []:
            self.page_signatures = ["page-%d"%(i) for i in range(2, self.pagesCrawlMax+1)]  
        self.toCrawlSignatures = [url.split('/')[-2] for url in self.toCrawl]


    def restartRun(self):

        self.runDuration = time.time()
        self.loadALL()
        self.pagesCrawled = 0
        self.linksCrawled = 0
        # print(type(self.toCrawl[0].split('/')))
        self.createSignatures()
        self.toCrawl = iter(self.toCrawl)


    def handle_request(self, response):

        self.crawl_parse(response)
        if (self.pagesCrawled >= self.pagesCrawlMax and self.no_linksToFetch == 0) :
            ioloop.IOLoop.instance().stop()


    def isListPage(self, response):
        # for part in response.request.url.split('/')[-2:]:
        #     if part in self.toCrawlSignatures:
        #         return True

        splitted = response.request.url.split('/')
        if ( (splitted[-2] in self.toCrawlSignatures) or (splitted[-2] in self.page_signatures) ):
            if "page" not in splitted[-2]:
                print("to crawl: ",splitted[-2])
            return True

        return False


    def crawl_parse(self, response):
        
        # allOld=False
        # new=0
        if self.isListPage(response) :
            # In case if response's url is the url for the ads list page

            if self.pagesCrawled >= self.pagesCrawlMax:
                self.printStats()
                return 

            parsed=self.Parser.parse(response, type=1)
            parsed_iter = {}
            for k,v in parsed.items():
                parsed_iter[k]=iter(v)

            # for link, date in zip(parsed['links'],parsed['dates']):
            for link in parsed['links']:
                id=self.extractID_fromLink(link)                    
                if id in self.allIds:
                    for k in parsed.keys():
                        next(parsed_iter[k])
                    continue

                else:
                    self.data[id]={}
                    for k in parsed.keys():
                        self.data[id][k]=next(parsed_iter[k])
                    
                    self.allIds.add(id)
                    url="http://www.kijiji.ca"+link
                    self.no_linksToFetch += 1 
                    self.http_client.fetch(url.strip(), self.handle_request, method='GET')

            self.pagesCrawled += 1          
            crawlNext=self.nextPage()
            if crawlNext != None and (not self.pagesCrawled >= self.pagesCrawlMax):
                self.http_client.fetch(crawlNext, self.handle_request, method='GET')

        else:
            # In case if response's url is the url for an individual ad's page
            parsed=self.Parser.parse(response, type=2)
            self.linksCrawled+=1
            self.no_linksToFetch -= 1 
            id = self.extractID_fromLink(response.request.url)
            # print(id)
            for k,v in parsed.items():
                self.data[id][k] = v

            # if self.linksCrawled >= self.linksCrawlMax:
            #     self.printStats()
            #     return 

        # for key in parsed.keys():
        #   print("For key = '%s', the following are extracted: "%(key))
        #   print(parsed[key])


    def nextPage(self):
        
        if self.pagesCrawled >= 1:
            next_page_str="page-"+str(self.pagesCrawled+1)
            url_splitted=self.current_URL.split('/')
            nextPage_link = '/'.join(url_splitted[0:-1] + [next_page_str] + [url_splitted[-1]])
            return nextPage_link

        else: 
            return None


    def printStats(self):
        print("Links crawled so far: ", self.linksCrawled)

    # def nextURL(self):
    #   """
    #   Decides what the next URL to crawl shall be and returns it.
    #   """
    #   pass


    # def scrape(self):
    #   """
    #   Responsible for extracting information from webpage.
    #   It depends on
    #   Returns a list containing the data extracted
    #   eg, [[item_name1, description], [item_name2, description] ,... ] 
    #   """
    #   pass

    # def inferFromData(self):

    #   pass


    def save(self):

        # Saving Data
        fileName =(self.saveDataDirectory
                 + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M') 
                 + ".pickle"
                  )

        with open(fileName, 'wb') as f:  
            pickle.dump([self.data, self.metaData], f)

        self.data = {}
        self.metaData = {}
        self.lastSaveTime = time.time()
        print("Saved at : %s"%(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))
        self.saveIDs()



    def loadALL(self):
        self.loadIDs()
        self.loadParams()

    def loadIDs(self):
        if os.path.isfile(self.IDsFileName):
            with open(self.IDsFileName, 'rb') as f:
                self.allIds = pickle.load(f) 


    def saveIDs(self):
        with open(self.IDsFileName, 'wb') as f:
            pickle.dump(self.allIds, f)


    def loadParams(self):

        # Loading params
        try:
            with open(self.paramsFileName, 'rb') as f:  
                allParams=pickle.load(f)

            self.toCrawlSize = len(allParams['toCrawl'])
            self.toCrawl=allParams['toCrawl']         
            self.savingPeriod=allParams['savingPeriod']             
            self.crawlPeriod=allParams['crawlPeriod'] * 3600
            self.numberOfRuns=allParams['numberOfRuns']
            self.saveDataDirectory=allParams['saveDataDirectory']           

        except Exception as e:

            print("ERROR! ", e)
            exit()


    def extractID_fromLink(self, link):
        splitted = link.split("/")
        id_str = splitted[-1].split("?")[0]
        if id_str.isdigit():
            return int(id_str)
        else:
            return id_str


    def loadEntityNames(self):
        f=open(self.entityListFileName, 'r')
        entities=f.read()
        self.entityList=entities.split(',')
        f.close()

    def isToSave(self):
        # Checks whether it is time to save
        if (self.runsSoFar % self.savingPeriod == 0) and (self.data != {}):  
            self.save()







class Parser():

    def __init__(self, parser_type=1):

        if parser_type==1:
            self.parse=self.parse_Normal

        self.pattern_dateListed='<span class="date-posted">.*</span>'
        pass


    def parse_Normal(self, response, type):
        """
        response is an object of tornado.httpclient.HTTPResponse class
        """

        soup = BeautifulSoup(response.body, 'html.parser')
        parsed={}
        # For parsing the advertisement list page( eg the list that has 20 Ads)
        if type == 1:

            titleLinks_response=soup.select('div.clearfix div.info div.info-container div.title a')
            parsed['titles']=[title.get_text().strip() for title in titleLinks_response]
            parsed['links']=[link.get('href').strip() for link in titleLinks_response]
            # print("number of links : ", len(parsed['links']))
            # for link in parsed['links']:
            #     print(link)
            dates=[]
            for item in soup.select("div.clearfix div.info div.info-container"):
                date_parsed = self.parse_date(str(item))
                if date_parsed == None:
                    dates=dates+[None]
                else:
                    dates=dates+date_parsed

            parsed['dates']=dates

            # parsed['titleLinks']=zip(titles,links)
            #Extracting the price of each item
            parsed['prices'] = [price.get_text().strip() for price in soup.select("div.clearfix div.info div.info-container div.price")];  


        # For parsing and extracting the descriptions from within a specific ad.
        elif type == 2:
            # desc = soup.select('div[id="UserContent"] span[itemprop="description"]')[0]
            # parsed['description'] = desc.get_text().strip()
            desc = soup.select('div[id="UserContent"] span[itemprop="description"]')
            if len(desc) == 0:
                # print("FOR TYPE 2, the URL : ", response.request.url)
                parsed['description'] = ""
            else:
                parsed['description'] = desc[0].get_text().strip()

        return parsed


    def parse_date(self, response_text):
        """
        Note that html.parser is needed for BeautifulSoup. Otherwise for datefields beginning with '<' wont be recognized
        """
        dates=[]
        for found in re.findall(self.pattern_dateListed, response_text):
            datePosted = re.match( r'<span class="date-posted">(.*)</span', found, re.M|re.I).group(1).strip()
            if datePosted[0:5] == '&lt; ':
                datePosted=datePosted[5:]
                splitted=datePosted.split(" ")
                time_=0
                if ("hours" or "hour") in splitted:
                    time_ += int(splitted[0].strip()) * 60
                if ("minutes" or "minute") in splitted:
                    time_ += int(splitted[0].strip())

                time_ *= 60 # Converting to seconds
                time_ = time.time() - time_
                dates.append(time_)

            else :
                splitted=datePosted.split("/")
                if len(splitted) == 3:
                    day = int(splitted[0])
                    month = int(splitted[1])
                    year = int(splitted[2])
                    dates.append( time.mktime(datetime.datetime(year, month, day).timetuple()) )

                else:
                    dates.append(datePosted)

        if len(dates) == 0:
            return None
        else:
            return dates


    def param_assertion(self, method, params):

        if method==self.__init__:
            possible_perserTypes=[1]
            assert(params["parser_type"] in possible_perserTypes), "Constructor 'input param': 'parser_type' not correct"



if __name__=="__main__":

    myCrawler=Crawler()
    myCrawler.runLoop()
