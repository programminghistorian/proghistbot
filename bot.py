import os
from tweepy import OAuthHandler, API
import random
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Test on Production
# Testing
# Test the tweets individually
# Fill out all the data
# Fill out the data with authors
# Restart the bot again
# Spanish translations will need to be entered either on
# their own spreadsheet with their own bots
# or just as their own rows here.
is_prod = os.environ.get('IS_HEROKU', None)

ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET')
CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')


def twitter_api():
    access_token = ACCESS_TOKEN
    access_token_secret = ACCESS_TOKEN_SECRET
    consumer_key = CONSUMER_KEY
    consumer_secret = CONSUMER_SECRET

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = API(auth)
    return api


def tweet(message):
    """Tweets"""
    print(message)
    api = twitter_api()
    api.update_status(status=message)


def get_tweet_contents_from_google():
    """Reads in contents of google spreadsheet."""
    scope = ['https://spreadsheets.google.com/feeds']

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'Programming Historian-aa456f0a6b33.json', scope)

    gc = gspread.authorize(credentials)
    wks = gc.open_by_key('1o-C-3WwfcEYWipIFb112tkuM-XOI8pVVpA9_sag9Ph8')
    list_of_items = wks.sheet1.get_all_values()[1:]

    return list_of_items


def select_random_lesson(lessons):
    """given a list of lessons, select one at random"""
    return random.choice(lessons)


def select_random_message(lesson):
    """Select one of the two options for messages"""
    choice = random.choice([1, 2])
    return lesson[choice]


def prepare_tweet():
    # options = get_tweet_contents_from_csv('tweet-manifest.csv')
    options = get_tweet_contents_from_google()
    lesson = select_random_lesson(options)
    message = select_random_message(lesson)
    link = lesson[3]
    return message + ' ' + link


def rest(max_sleep):
    time.sleep(random.random() * max_sleep)


def main():

    tweet_contents = prepare_tweet()

    try:
        tweet(tweet_contents)
        print('Success: ' + tweet_contents)
    except:
        print('Fail: ' + tweet_contents)


if __name__ == '__main__':
    main()
