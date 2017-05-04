import os
from tweepy import OAuthHandler, API
import random
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Test on Production
# Testing
# rather than randomly choosing b/w lessons one and two you'll want
# to say, look at column A. Find the X's. Now find the one X that is missing a
# Y. tweet that message two.
# Make sure it is still tweeting
# When tweets are full it's not wiping out the one with the Y.
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
        'Programming_Historian-aa456f0a6b33.json', scope)

    gc = gspread.authorize(credentials)
    wks = gc.open_by_key('1o-C-3WwfcEYWipIFb112tkuM-XOI8pVVpA9_sag9Ph8')
    list_of_items = wks.sheet1.get_all_values()[1:5]

    return wks.sheet1, list_of_items


def update_sheet_queue_after_tweeting(sheet, id_num):
    """After a tweet has been sent out, update the spreadsheet.
    Add two to make the cells line up. Most recent tweet marked with
    XY"""

    cell_label = 'E' + str(int(id_num) + 2)
    print(cell_label)
    sheet.update_acell(cell_label, 'XY')


def remove_last_tweet_marker(lessons, sheet):
    """Remove the last tweet marker XY and replace with just X."""
    for lesson in lessons:
        if lesson[4].endswith('Y'):
            sheet.update_acell('E' + str(int(lesson[0]) + 2), 'X')
    pass


def clear_queue(sheet, id_num):
    cell_label = 'E' + str(int(id_num) + 2)
    sheet.update_acell(cell_label, '')


def select_random_lesson(lessons, sheet):
    """given a list of lessons, select one at random"""

    remaining_lessons = [
        lesson for lesson in lessons if not lesson[4].startswith('X')]
    if not remaining_lessons:
        print('all out!')
        for id_num in [lesson[0] for lesson in lessons]:
            clear_queue(sheet, id_num)
        the_choice = random.choice(lessons)
    else:
        print('some stuff remaining')
        the_choice = random.choice(remaining_lessons)
    return the_choice


def select_random_message(lesson):
    """Select one of the two options for messages"""
    choice = random.choice([1, 2])
    return lesson[choice]


def prepare_tweet():
    # options = get_tweet_contents_from_csv('tweet-manifest.csv')
    sheet, options = get_tweet_contents_from_google()
    lesson = select_random_lesson(options, sheet)
    message = select_random_message(lesson)
    link = lesson[3]
    # Something wonky going on here. get it to print out some variables of
    # things you're tweeting. somehow it is marking things twice.
    remove_last_tweet_marker(options, sheet)
    update_sheet_queue_after_tweeting(sheet, lesson[0])
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
