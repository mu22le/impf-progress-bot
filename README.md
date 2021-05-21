# Impfstatus Fortschritt Twitter Bot

This is a somewhat modified version of [@impf_progress](https://twitter.com/impf_progress) it reads its data from ourworldindata.org, so it can easily be modified to tweet the stats for any countr or region.

## Script Setup

- Create an app at the [Twitter Developer site](https://developer.twitter.com/) and create app tokens and keys
- Edit [twitter.cfg](./twitter.cfg) and put in your Twitter Consumer and Access tokens/keys
- Make sure [state.cfg](./state.cfg) is writable, this is where the last Tweet and its values are stored so to not Tweet repeated messages
- Change `DRY_RUN = True` in [bot.py](./bot.py) to `False` when you are done testing
- Install Tweepy and Pandas, using virtualenv

```
# Create venv
py -3 venv venv

# Activate venv: Windows
venv\Scripts\activate.bat 

# Activate venv: Linux
venv\bin\activate

# Install tweepy directly
pip3 install tweepy pandas

# Alternatively, use requirements.txt
pip install -r requirements.txt
```

The script can now simply be called like this:

```
python bot.py
# or
py -3 bot.py
```

## Crontab Setup

Running a cronjob with virtualenv:

```
0 12 * * * cd /home/you/impf-progress-bot/ && /home/you/impf-progress-bot/venv/bin/python /home/you/impf-progress-bot/bot.py
```

## Data Source

Mathieu, E., Ritchie, H., Ortiz-Ospina, E. et al. A global database of COVID-19 vaccinations. Nat Hum Behav (2021) 

## License

MIT
