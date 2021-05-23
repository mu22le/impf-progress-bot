# from tweetbot.tweetbot import VaxTweetBot
from tweetbot.tweetbot_it import VaxTweetBotIt

DRY_RUN = True

VaxTweetBot(dry_run = DRY_RUN).runAll()
# VaxTweetBotIt(dry_run = DRY_RUN).runAll()
