import pandas as pd
from .tweetbot import VaxTweetBot
from datetime import date
from datetime import timedelta
import locale

class VaxTweetBotIt(VaxTweetBot):

    def __init__(self, dry_run = True, conf_file = 'state.cfg', key_file = 'twitter.cfg') -> None:
        super().__init__(dry_run=dry_run, conf_file=conf_file, key_file=key_file)
        
        self.loc='Italia'
        self.url='https://github.com/italia/covid19-opendata-vaccini/raw/master/dati/anagrafica-vaccini-summary-latest.csv'
        self.hist_url='https://github.com/italia/covid19-opendata-vaccini/raw/master/dati/somministrazioni-vaccini-summary-latest.csv'

    def getCurrentdata(self):
        df = pd.read_csv(self.url)
        italian_pop = 59257566 #http://dati.istat.it/Index.aspx?DataSetCode=DCIS_POPRES1
        self.data = {'date':df.ultimo_aggiornamento.max(),
                'vaccinated_first': df.prima_dose.sum()/italian_pop*100,
                'vaccinated_full': df.seconda_dose.sum()/italian_pop*100,
        }
        df=pd.read_csv(self.hist_url)
        fvax_per_day = (df.groupby('data_somministrazione').seconda_dose.sum()).rolling(window=7).mean()[-2]
        fvax_tot = self.data['vaccinated_full']
        herd_imm_thrs = 0.7
        herd_imm_pop = italian_pop*herd_imm_thrs
        days_to_herd_imm = round( (herd_imm_pop - fvax_tot) / fvax_per_day )
        herd_imm_date = date.today() + timedelta(days=days_to_herd_imm)
        locale.setlocale(locale.LC_ALL, "it_IT")
        self.data['herd_imm_date'] = herd_imm_date.strftime("%B %Y")


    def generateMessage(self, ):
        bar_first = self.generateProgressbar(float(self.data['vaccinated_first']))
        bar_full = self.generateProgressbar(float(self.data['vaccinated_full']), color='blue')
        msg = f'#Vaccini anti #Covid19 in {self.loc}:\n' + \
        f'{bar_first} vaccinati\n' + \
        f'{bar_full} completamente vaccinati\n' + \
        f'Di questo passo #immunitàdigregge (70%) per {self.data["herd_imm_date"]}'
        return msg
