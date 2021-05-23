# Vaccine progress bar Twitter Bot

This is a somewhat modified version of [@impf_progress](https://twitter.com/impf_progress) it reads its data from ourworldindata.org, so it can easily be used to tweet the stats for any country or region.

If you want to use local sources (usually more up-to-date) write your own getCurrentdata() function. You can see an example of this in tweetbot_it, where I get the data from [covid19-opendata-vaccini](https://github.com/italia/covid19-opendata-vaccini).

## Script Setup

- Create an app at the [Twitter Developer site](https://developer.twitter.com/) and create app tokens and keys
- Edit [twitter.cfg](./twitter.cfg) and put in your Twitter Consumer and Access tokens/keys
- Make sure [state.cfg](./state.cfg) is writable, this is where the last Tweet and its values are stored so to not Tweet repeated messages
- Edit [state.cfg](./state.cfg) to select your favourite country/area
- Install Tweepy and Pandas
- Change `DRY_RUN = True` in [run_bot.py](./run_bot.py) to `False` when you are done testing


```
# Install tweepy directly
pip3 install tweepy pandas

# Alternatively, use requirements.txt
pip install -r requirements.txt
```

The script can now simply be called like this:

```
python run_bot.py
```

## Crontab Setup

Running a cronjob with virtualenv:

```
0 12 * * * cd /home/you/impf-progress-bot/ && /bin/python /home/you/impf-progress-bot/run_bot.py
```

## Data Source

Mathieu, E., Ritchie, H., Ortiz-Ospina, E. et al. A global database of COVID-19 vaccinations. Nat Hum Behav (2021) 

## License

MIT
