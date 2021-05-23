import tweepy
from datetime import datetime
import configparser
import pandas as pd
from math import isnan


class VaxTweetBot():
    '''
    A class that downloads the latest COVID-19 vaccination data from ourworld in data and tweets them
    '''
    DRY_RUN = True

    def __init__(self, dry_run = True, conf_file = 'state.cfg', key_file = 'twitter.cfg') -> None:
        twitter_config = configparser.ConfigParser()
        twitter_config.read(key_file)
        CONSUMER_KEY    = twitter_config.get('TWITTER', 'CONSUMER_KEY')
        CONSUMER_SECRET = twitter_config.get('TWITTER', 'CONSUMER_SECRET')
        ACCESS_KEY      = twitter_config.get('TWITTER', 'ACCESS_KEY')
        ACCESS_SECRET   = twitter_config.get('TWITTER', 'ACCESS_SECRET')
        self.auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        self.auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)

        self.config = configparser.ConfigParser()
        self.config.read(conf_file)
        self.loc = self.config.get('CONF', 'location')
        self.url = self.config.get('CONF', 'url')
        self.conf_file = conf_file

        self.DRY_RUN = dry_run

    def generateProgressbar(self, percentage):
        num_chars = 14
        num_filled = round(percentage*num_chars/100)
        num_empty = num_chars-num_filled
        display_percentage = str(round(percentage, 1)).replace('.', ',')
        progress_bar = f"{'🟩'*num_filled}{'⬜'*num_empty}"
        # if herd_immunity :
        #     hi_mark = int(num_chars*herd_immunity)
        #     progress_bar = progress_bar[:hi_mark]+'|'+progress_bar[hi_mark:]
        msg = f'{progress_bar} {display_percentage}%'
        # msg = '{}{} {}%'.format('▓'*num_filled, '░'*num_empty, display_percentage)
        return msg

    def getCurrentdata(self):
        df = pd.read_csv(self.url)
        latest = df.loc[df.location==self.loc, 'date'].max()
        line = df.loc[df.location==self.loc].loc[ df.date==latest]
        self.data = {'date': line.date.values[0],
                'vaccinated_first': line.people_vaccinated_per_hundred.values[0],
                'vaccinated_full': line.people_fully_vaccinated_per_hundred.values[0],
        }

    def sendTweet(self, the_tweet):
        twitter_API = tweepy.API(self.auth)
        print('tweeting with handle @{}'.format(twitter_API.me().screen_name))
        if self.DRY_RUN:
            print("DRY RUN not actually sending tweet!")
            return
        twitter_API.update_status(the_tweet)

    def checkIfShouldTweet(self, ):
        if isnan(self.data['vaccinated_first']) or isnan(self.data['vaccinated_full']):
            print("No data available yet today")
            return False

        last_date = datetime.strptime(self.config.get('LAST_TWEET', 'date'), '%Y-%m-%d')
        curr_date = datetime.strptime(self.data['date'], '%Y-%m-%d')
        print("date: {} / {}".format(self.config.get('LAST_TWEET', 'date'), self.data['date']))

        vaccinated_old = float(self.config.get('LAST_TWEET', 'vaccinated_first'))
        fully_vaccinated_old = float(self.config.get('LAST_TWEET', 'vaccinated_full'))
        vaccinated_new = float(self.data['vaccinated_first'])
        fully_vaccinated_new = float(self.data['vaccinated_full'])
        
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

    def saveState(self, ):
        self.config.set('LAST_TWEET', 'date', self.data['date'])
        self.config.set('LAST_TWEET', 'vaccinated_first', str(self.data['vaccinated_first']))
        self.config.set('LAST_TWEET', 'vaccinated_full', str(self.data['vaccinated_full']))
        if self.DRY_RUN :
            print("DRY RUN, not actually saving conf!")
        else:
            with open(self.conf_file, 'w') as configfile:
                self.config.write(configfile)
                print("saved cfg")

    def generateMessage(self, ):
        bar_first = self.generateProgressbar(float(self.data['vaccinated_first']))
        bar_full = self.generateProgressbar(float(self.data['vaccinated_full']))
        msg = f'{self.loc}:\n{bar_first} vaccinated\n{bar_full} fully vaccinated'
        return msg

    def runAll(self):
        data = self.getCurrentdata()
        should_send = self.checkIfShouldTweet()
        print("send tweet?", should_send)
        if should_send:
            # need to tweet
            print('send tweet:\n')
            progress_msg = self.generateMessage()
            print(progress_msg,'\n')
            self.sendTweet(progress_msg)
        else:
            print('do not tweet')
        self.saveState()


