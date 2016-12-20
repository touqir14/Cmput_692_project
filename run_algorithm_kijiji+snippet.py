import builtins
import kijiji_snippets_settings
from algorithms import *

builtins.SETTINGS = kijiji_snippets_settings

if __name__ == "__main__":
	generate_IDF()
	generate_correlationScores()
