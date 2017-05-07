import os
import sys
import argparse
from tweepy import OAuthHandler, API
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import traceback


# look into encrypting the stuff in the json -
# https://github.com/andrewcooke/simple-crypt
# Scheduling - it's a daily task that only runs certain days of the week.
# Monday - 9AM PST, 12PM EST, 4PM London time
# if [ "$(date +%u)" = 1 ]; then python bot.py; fi
# Thursday 6:30 AM PST, 9:30 AM EST, 1:30PM London
# if [ "$(date +%u)" = 4 ]; then python bot.py -t True; fi
# TODO: better error testing, since it can't persistently write to files
# TODO: use for whole list of tweets once you're positive it's working.
# TODO: Spanish as its own sheet
# TODO: Can you remove the ID column?
# Test on Production
# Testing
# Make sure it is still tweeting
# Test the tweets individually
# Fill out all the data
# Fill out the data with authors
# Spanish translations can probably just be their own sheet. All else can remain the same.

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
    list_of_items = wks.sheet1.get_all_values()[:5]
    headers = list_of_items.pop(0)

    return wks.sheet1, pd.DataFrame(list_of_items, columns=headers)


def update_sheet_queue_after_tweeting(sheet, id_num):
    """After a tweet has been sent out, update the spreadsheet.
    Add two to make the cells line up. Most recent tweet marked with
    XY"""
    cell_label = 'E' + str(int(id_num.values[0]) + 2)
    print('========')
    print('update_sheet_queue')
    print(cell_label)
    print('========')
    sheet.update_acell(cell_label, 'XY')


def remove_last_tweet_marker(lessons_frame, sheet):
    """Remove the last tweet marker XY and replace with just X."""
    last_tweet = lessons_frame.tweet_log.str.endswith('Y')
    print('looking for last markers')
    if lessons_frame[last_tweet].index.any() or \
            lessons_frame[last_tweet].index.values[0] == 0:
        print('found one')
        for index_num in lessons_frame[last_tweet].index.values:
            cell_label = 'E' + str(index_num + 2)
            print('=====')
            print('remove_last_tweet_marker')
            print(cell_label)
            print('=====')
            sheet.update_acell(cell_label, 'X')
    else:
        print('could not find any')
        print(lessons_frame[last_tweet].index)
        pass


def clear_queue(sheet, id_num):
    cell_label = 'E' + str(int(id_num) + 2)
    print('======')
    print('cleaning_queue')
    print(cell_label)
    print('======')
    sheet.update_acell(cell_label, '')


def select_random_lesson(lessons_frame, sheet):
    """given a list of lessons, select one at random"""

    # so all False - needs to be purged because everything has been tweeted.
    remaining_lessons = ~lessons_frame.tweet_log.str.startswith('X')
    if remaining_lessons.any():
        print('some stuff remaining')
        the_choice = lessons_frame.iloc[[random.choice(
            lessons_frame[remaining_lessons]
            .index.values)]]
    else:
        print('all out!')
        for id_num in lessons_frame.index.values:
            clear_queue(sheet, id_num)
        the_choice = lessons_frame.iloc[[random.choice(
            lessons_frame.index.values)]]
    return the_choice


def select_first_message(lesson):
    """Select one of the two options for messages"""
    return lesson.message_one.values[0]


def select_second_message(lesson):
    return lesson.message_two.values[0]


def prepare_tweet(day_two=False, spanish=False):
    sheet, options_frame = get_tweet_contents_from_google()
    remove_last_tweet_marker(options_frame, sheet)
    if day_two:
        last_tweet = options_frame.tweet_log.str.endswith('Y')
        lesson = options_frame[last_tweet]
        message = select_second_message(lesson)
    else:
        lesson = select_random_lesson(options_frame, sheet)
        message = select_first_message(lesson)
    link = lesson.link.values[0]
    update_sheet_queue_after_tweeting(sheet, lesson.index)
    return message + ' ' + link


def parse_args(argv=None):
    """This parses the command line."""
    argv = sys.argv[1:] if argv is None else argv
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('-t', '--two', dest='day_two', action='store',
                        default=False,
                        help='Set tweets for second message')
    parser.add_argument('-es', '--spanish', dest='spanish', type=bool,
                        default=False,
                        help='Set tweets to be Spanish. '
                        'Default = False')
    return parser.parse_args(argv)


def main():
    args = parse_args()
    tweet_contents = prepare_tweet(args.day_two, args.spanish)

    try:
        tweet(tweet_contents)
        print('Success: ' + tweet_contents)
    except:
        print('Fail: ' + tweet_contents + '\n')
        print(traceback.format_exc())
        with open('errors.txt', 'a') as fn:
            print('===========')
            print(tweet_contents + '\n')
            print('===========')
            fn.write('===========')
            fn.write('Fail: ' + tweet_contents + '\n')
            fn.write(traceback.format_exc() + '\n')
            fn.write('===========' + '\n')


if __name__ == '__main__':
    main()
