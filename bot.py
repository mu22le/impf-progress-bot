import csv
import urllib.request
import tweepy
from datetime import datetime
import configparser
import pandas as pd

DRY_RUN = True

twitter_config = configparser.ConfigParser()
twitter_config.read('twitter.cfg')
CONSUMER_KEY    = twitter_config.get('TWITTER', 'CONSUMER_KEY')
CONSUMER_SECRET = twitter_config.get('TWITTER', 'CONSUMER_SECRET')
ACCESS_KEY      = twitter_config.get('TWITTER', 'ACCESS_KEY')
ACCESS_SECRET   = twitter_config.get('TWITTER', 'ACCESS_SECRET')
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)

url = 'https://covid.ourworldindata.org/data/owid-covid-data.csv'
loc = 'Italy'

CONFIG_FILENAME = 'state.cfg'

config = configparser.ConfigParser()
config.read(CONFIG_FILENAME)

def generateProgressbar(percentage):
	num_chars = 15
	num_filled = round(percentage*num_chars)
	num_empty = num_chars-num_filled
	display_percentage = str(round(percentage*100, 1))
	msg = '{}{} {}%'.format('▓'*num_filled, '░'*num_empty, display_percentage)
	return msg

def getCurrentdata(url):
	df = pd.read_csv(url)
	today = df.loc[df.location==loc, 'date'].max()
	return df.loc[df.location==loc].loc[ df.date==today]

def sendTweet(the_tweet):
	twitter_API = tweepy.API(auth)
	print('tweeting with handle @{}'.format(twitter_API.me().screen_name))
	if DRY_RUN:
		print("DRY RUN not actually sending tweet!")
		return
	twitter_API.update_status(the_tweet)

def checkIfShouldTweet(data):
	last_date = datetime.strptime(config.get('LAST_TWEET', 'date'), '%Y-%m-%d')
	curr_date = datetime.strptime(data.date.values[0], '%Y-%m-%d')
	print("date: {} / {}".format(config.get('LAST_TWEET', 'date'), data.date.values[0]))

	if last_date < curr_date:
		vaccinated_old = float(config.get('LAST_TWEET', 'vaccinated_first'))
		fully_vaccinated_old = float(config.get('LAST_TWEET', 'vaccinated_full'))
		vaccinated_new = float(data.people_vaccinated_per_hundred)
		fully_vaccinated_new = float(data.people_fully_vaccinated_per_hundred)
		
		print("vaccinated: {} / {}".format(round(vaccinated_old, 1), round(vaccinated_new, 1)))
		print("fully: {} / {}".format(round(fully_vaccinated_old, 1), round(fully_vaccinated_new, 1)))
		
		if round(vaccinated_old, 1) < round(vaccinated_new, 1):
			return True
		if round(fully_vaccinated_old, 1) < round(fully_vaccinated_new, 1):
			return True
		return False
	else:
		print("date is same or older: do not tweet")
		return False

def saveState(data):
	config.set('LAST_TWEET', 'date', data.date.values[0])
	config.set('LAST_TWEET', 'vaccinated_first', data.people_vaccinated_per_hundred)
	config.set('LAST_TWEET', 'vaccinated_full', data.people_fully_vaccinated_per_hundred)
	with open(CONFIG_FILENAME, 'w') as configfile:
		config.write(configfile)
		print("saved cfg")

def generateMessage(data):
	bar_first = generateProgressbar(float(data.people_vaccinated_per_hundred/100))
	bar_full = generateProgressbar(float(data.people_fully_vaccinated_per_hundred/100))
	msg = f'{loc}:\n{bar_first} vaccinated\n{bar_full} fully vaccinated'
	return msg

def runAll():
	data = getCurrentdata(url)
	should_send = checkIfShouldTweet(data)
	print("send tweet?", should_send)
	if should_send:
		# need to tweet
		print('send tweet:')
		print('')
		progress_msg = generateMessage(data)
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
