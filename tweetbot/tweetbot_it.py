import pandas as pd
from .tweetbot import VaxTweetBot

class VaxTweetBotIt(VaxTweetBot):

    def __init__(self, dry_run = True, conf_file = 'state.cfg', key_file = 'twitter.cfg') -> None:
        super().__init__(dry_run=dry_run, conf_file=conf_file, key_file=key_file)
        
        self.loc='Italia'
        self.url='https://github.com/italia/covid19-opendata-vaccini/raw/master/dati/anagrafica-vaccini-summary-latest.csv'

    def getCurrentdata(self):
        df = pd.read_csv(self.url)
        italian_pop = 60.36e6
        self.data = {'date':df.ultimo_aggiornamento.max(),
                'vaccinated_first': df.prima_dose.sum()/italian_pop*100,
                'vaccinated_full': df.seconda_dose.sum()/italian_pop*100,
        }

    def generateMessage(self, ):
        bar_first = self.generateProgressbar(float(self.data['vaccinated_first']))
        bar_full = self.generateProgressbar(float(self.data['vaccinated_full']))
        msg = f'{self.loc}:\n{bar_first} vaccinati\n{bar_full} completamente vaccinati'
        return msg
