import pickle

# toCrawl is a list of root pages to start crawling.
toCrawl=["http://www.kijiji.ca/b-buy-sell/alberta/c10l9003",
		 "http://www.kijiji.ca/b-buy-sell/british-columbia/c10l9007",
		 "http://www.kijiji.ca/b-buy-sell/manitoba/c10l9006",
		 "http://www.kijiji.ca/b-buy-sell/new-brunswick/c10l9005",
		 "http://www.kijiji.ca/b-buy-sell/newfoundland/c10l9008",
		 "http://www.kijiji.ca/b-buy-sell/nova-scotia/c10l9002",
		 "http://www.kijiji.ca/b-buy-sell/ontario/c10l9004",
		 "http://www.kijiji.ca/b-buy-sell/prince-edward-island/c10l9011",
		 "http://www.kijiji.ca/b-achat-et-vente/quebec/c10l9001",
		 "http://www.kijiji.ca/b-buy-sell/saskatchewan/c10l9009",
		 "http://www.kijiji.ca/b-buy-sell/territories/c10l9010"]

temptoCrawl = ["http://www.kijiji.ca/b-buy-sell/alberta/c10l9003",
		 "http://www.kijiji.ca/b-buy-sell/british-columbia/c10l9007"]

# In the crawler code, they are converted to seconds, so no need to multiply with 3600
savingPeriod = 1 # FREQUENCY: at the end of every run
crawlPeriod = 1 # HOUR : every hour.

numberOfRuns = 960 #Number of crawling sessions after which the crawler will exit.
saveDataDirectory = "/cshome/touqir/cmput_692/cmput_692_project/data/collected_data/"

allParams={ 
			'toCrawl' : toCrawl, #######################################____WATCH OUT_____________________
			'savingPeriod' : savingPeriod, 
			'crawlPeriod' : crawlPeriod, 
			'numberOfRuns' : numberOfRuns,
			'saveDataDirectory' : saveDataDirectory
		  }



def gen_pickle():
	"""
												!!!REMEMBER!!!  

	If you called this function from python/ipython by first importing params.py and invoking the function and you made changes
	to this file , please restart python/ipython and import params.py again to invok gen_pickle. Otherwise calling gen_pickle uses the old
	params.py which doesnt contain your recent changes

												!!!REMEMBER!!!  

	"""

	with open( "params.pickle", "wb" ) as f :
		pickle.dump(allParams, f)



if __name__=="__main__":
	gen_pickle()
