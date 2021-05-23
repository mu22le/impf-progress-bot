import tweepy
from datetime import datetime
import configparser
import pandas as pd
from math import isnan

DRY_RUN = True

twitter_config = configparser.ConfigParser()
twitter_config.read('twitter.cfg')
CONSUMER_KEY    = twitter_config.get('TWITTER', 'CONSUMER_KEY')
CONSUMER_SECRET = twitter_config.get('TWITTER', 'CONSUMER_SECRET')
ACCESS_KEY      = twitter_config.get('TWITTER', 'ACCESS_KEY')
ACCESS_SECRET   = twitter_config.get('TWITTER', 'ACCESS_SECRET')
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)


#  Mathieu, E., Ritchie, H., Ortiz-Ospina, E. et al. A global database of COVID-19 vaccinations. Nat Hum Behav (2021) 
url = 'https://covid.ourworldindata.org/data/owid-covid-data.csv'

CONFIG_FILENAME = 'state.cfg'

config = configparser.ConfigParser()
config.read(CONFIG_FILENAME)

def generateProgressbar(percentage, herd_immunity=0):
	num_chars = 14
	num_filled = round(percentage*num_chars/100)
	num_empty = num_chars-num_filled
	display_percentage = str(round(percentage, 1)).replace('.', ',')
	progress_bar = f"{'🟩'*num_filled}{'⬜'*num_empty}"
	if herd_immunity :
		hi_mark = int(num_chars*herd_immunity)
		progress_bar = progress_bar[:hi_mark]+'|'+progress_bar[hi_mark:]
	msg = f'{progress_bar} {display_percentage}%'
	# msg = '{}{} {}%'.format('▓'*num_filled, '░'*num_empty, display_percentage)
	return msg

def getCurrentdata(url, loc):
	df = pd.read_csv(url)
	today = df.loc[df.location==loc, 'date'].max()
	line = df.loc[df.location==loc].loc[ df.date==today]
	data = {'date':line.date.values[0],
			'vaccinated_first': line.people_vaccinated_per_hundred.values[0],
			'vaccinated_full': line.people_fully_vaccinated_per_hundred.values[0],
	}

	print(data)
	return data

def sendTweet(the_tweet):
	twitter_API = tweepy.API(auth)
	print('tweeting with handle @{}'.format(twitter_API.me().screen_name))
	if DRY_RUN:
		print("DRY RUN not actually sending tweet!")
		return
	twitter_API.update_status(the_tweet)

def loadConf():
	loc = config.get('CONF', 'location')
	return loc


def checkIfShouldTweet(data):
	if isnan(data['vaccinated_first']) or isnan(data['vaccinated_full']):
		print("No data available yet today")
		return False

	last_date = datetime.strptime(config.get('LAST_TWEET', 'date'), '%Y-%m-%d')
	curr_date = datetime.strptime(data['date'], '%Y-%m-%d')
	print("date: {} / {}".format(config.get('LAST_TWEET', 'date'), data['date']))

	vaccinated_old = float(config.get('LAST_TWEET', 'vaccinated_first'))
	fully_vaccinated_old = float(config.get('LAST_TWEET', 'vaccinated_full'))
	vaccinated_new = float(data['vaccinated_first'])
	fully_vaccinated_new = float(data['vaccinated_full'])
	
	print(f"vaccinated: {round(vaccinated_old, 1)} / {round(vaccinated_new, 1)}")
	print(f"fully: {round(fully_vaccinated_old, 1)} / {round(fully_vaccinated_new, 1)}")

	if last_date != curr_date:
		return True
	elif round(vaccinated_old, 1) < round(vaccinated_new, 1):
		return True
	elif round(fully_vaccinated_old, 1) < round(fully_vaccinated_new, 1):
		return True
	else:
		print("date is same or older: do not tweet")
		return False

def saveState(data):
	config.set('LAST_TWEET', 'date', data['date'])
	config.set('LAST_TWEET', 'vaccinated_first', str(data['vaccinated_first']))
	config.set('LAST_TWEET', 'vaccinated_full', str(data['vaccinated_full']))
	if DRY_RUN :
		print("DRY RUN not actually saving conf!")
	else:
		with open(CONFIG_FILENAME, 'w') as configfile:
			config.write(configfile)
			print("saved cfg")

def generateMessage(data, loc):
	bar_first = generateProgressbar(float(data['vaccinated_first']))
	bar_full = generateProgressbar(float(data['vaccinated_full']))
	msg = f'{loc}:\n{bar_first} vaccinated\n{bar_full} fully vaccinated'
	return msg

def runAll():
	loc = loadConf()
	data = getCurrentdata(url, loc)
	should_send = checkIfShouldTweet(data)
	print("send tweet?", should_send)
	if should_send:
		# need to tweet
		print('send tweet:')
		print('')
		progress_msg = generateMessage(data, loc)
		print(progress_msg)
		print('')
		sendTweet(progress_msg)
	else:
		print('do not tweet')
	saveState(data)

try:
	runAll()
except:
	raise
