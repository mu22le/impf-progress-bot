import pandas as pd
from .tweetbot import VaxTweetBot
from datetime import date
from datetime import timedelta
import locale


class VaxTweetBotIt(VaxTweetBot):
    '''
    This class specializes VaxTweetBot to the Italian case. 
    It gets data from the gov repos, which are utdated more often
    and adds computation of her immunity date to the mix.
    '''

    def __init__(self, dry_run=True, conf_file='state.cfg', key_file='twitter.cfg') -> None:
        '''
        Itialise the bot. 
        Some information, such as the data repo urls are not read from the config. 
        '''
        super().__init__(dry_run=dry_run, conf_file=conf_file, key_file=key_file)

        self.loc = 'Italia'
        self.url = 'https://github.com/italia/covid19-opendata-vaccini/raw/master/dati/anagrafica-vaccini-summary-latest.csv'
        self.hist_url = 'https://github.com/italia/covid19-opendata-vaccini/raw/master/dati/somministrazioni-vaccini-summary-latest.csv'

    def getCurrentdata(self):
        '''
        Get the raw data from the italian public repos and compute
        the dayly stats and the herd immunity date.

        The herd immunity date uses a 14 days rolling average ignoring the last day.
        It is at best an educated guess given that:
         - it assumes immunity lasts forever
         - it does not account for the accelerating pace of vaccinations.
         - it does not account for vaccine skepticism in the population.
         - it assumes all vaccines require 2 doses (not true for J&J).
         - it assumes doses are always spaced by 5 weeks (not true for AZ)
         - it probably make other assumptions I'm not aware of.
        '''
        # get latest vaccination numbers
        df = pd.read_csv(self.url)
        italian_pop = 59257566  # http://dati.istat.it/Index.aspx?DataSetCode=DCIS_POPRES1
        self.data = {'date': df.ultimo_aggiornamento.max(),
                     'vaccinated_first': df.prima_dose.sum()/italian_pop*100,
                     'vaccinated_full': df.seconda_dose.sum()/italian_pop*100,
                     }
        # get historical vaccinations
        df = pd.read_csv(self.hist_url)
        # get rolling mean of daily full vaccinations up to yesterday
        # (today's data may be incomplete)
        vax_per_day = (df.groupby('data_somministrazione').totale.sum()).rolling(
            window=7).mean()[-1]/2
        vax_tot = df.totale.sum()/2
        herd_imm_thrs = 0.7
        herd_imm_pop = italian_pop*herd_imm_thrs
        # (n of people to vaccinate to get to 70%) / (vax speed)
        days_to_herd_imm = round((herd_imm_pop - vax_tot) / vax_per_day)
        # get expected herd immunity day, but print month only
        herd_imm_date = date.today() + timedelta(days=days_to_herd_imm) + timedelta(weeks=5)
        locale.setlocale(locale.LC_ALL, "it_IT")
        self.data['herd_imm_date'] = herd_imm_date.strftime("%B %Y")
        self.data['does today'] = df.groupby(
            'data_somministrazione').totale.sum()[-1]

    def generateMessage(self, ):
        '''
        Put all the info together in a nice looking (I hope) tweet
        '''
        # get progress bars
        bar_first = self.generateProgressbar(
            float(self.data['vaccinated_first']))
        bar_full = self.generateProgressbar(
            float(self.data['vaccinated_full']), color='blue')
        # assemble tweet
        msg = f'#Vaccini anti #Covid19 in {self.loc}:\n' + \
            f'{bar_first} vaccinati\n' + \
            f'{bar_full} completamente vaccinati\n' + \
            f'Di questo passo #immunitàdigregge (70%) per {self.data["herd_imm_date"]}'
        return msg
