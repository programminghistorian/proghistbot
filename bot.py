from __future__ import unicode_literals
import os
import sys
import argparse
from tweepy import OAuthHandler, API
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import traceback
import time

# TODO: Refactor to remove the ID column, since Pandas can make one for us.
# TODO: Schedule a Spanish worker on Heroku
# if [ "$(date +%u)" = 2 ]; then python bot.py -es True; fi

ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET')
CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')


def rest(max_sleep):
    """Rest after tweeting - used when testing. """
    time.sleep(random.random() * max_sleep)


def twitter_api():
    """Initialize Twitter API, authorize, and return a usable object."""
    access_token = ACCESS_TOKEN
    access_token_secret = ACCESS_TOKEN_SECRET
    consumer_key = CONSUMER_KEY
    consumer_secret = CONSUMER_SECRET

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = API(auth)
    return api


def tweet(message):
    """Tweets a prepared message using the authorized API."""
    print(message)
    api = twitter_api()
    api.update_status(status=message)


def get_tweet_contents_from_google(spanish=False):
    """Reads in contents of google spreadsheet. Returns both the
    spreadshet for updating and a Pandas dataframe of the data
    for working with."""
    scope = ['https://spreadsheets.google.com/feeds']

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'proghist-google-credentials.json', scope)

    gc = gspread.authorize(credentials)
    wks = gc.open_by_key('1o-C-3WwfcEYWipIFb112tkuM-XOI8pVVpA9_sag9Ph8')
    if spanish:
        print('tweeting in spanish')
        list_of_items = wks.worksheet('Spanish').get_all_values()
        headers = list_of_items.pop(0)
        return wks.worksheet('Spanish'), pd.DataFrame(list_of_items, columns=headers)
    else:
        print('tweeting in english')
        list_of_items = wks.sheet1.get_all_values()
        headers = list_of_items.pop(0)
        return wks.sheet1, pd.DataFrame(list_of_items, columns=headers)


def update_sheet_queue_after_tweeting(sheet, id_num):
    """After a tweet has been sent out, update the spreadsheet.
    Add two to make the cells line up with the indexing of the data.
    Most recent tweet is marked with XY, so as to distinguish it from
    the rest of the previous tweets that are marked with X."""
    cell_label = 'E' + str(int(id_num.values[0]) + 2)
    print('========')
    print('update_sheet_queue')
    print(cell_label)
    print('========')
    sheet.update_acell(cell_label, 'XY')


def remove_last_tweet_marker(lessons_frame, sheet):
    """Remove the tweet marker XY from the previous tweet and
    replace with just X. Also catches a couple bugs - will remove multiple
    XY markers if they exist (though I fixed that problem), and will log if
    there don't appear to be any last tweet markers."""
    last_tweet = lessons_frame.tweet_log.str.endswith('Y')
    print('looking for last markers')
    print(lessons_frame[last_tweet])
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
        print('could not find any last tweet markers')
        print(lessons_frame[last_tweet].index)
        pass


def clear_queue(sheet, id_num):
    """Cleans out the Tweet log when everything has been tweeted so that
    the tweet queue will restart."""
    cell_label = 'E' + str(int(id_num) + 2)
    print('======')
    print('cleaning_queue')
    print(cell_label)
    print('======')
    sheet.update_acell(cell_label, '')


def select_random_lesson(lessons_frame, sheet):
    """Given a list of lessons, select one at random from those that haven't
    been tweeted. If there are none left, clear the queue and pick a random one
    from the new set."""
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
    """Select the first message of a given lesson."""
    return lesson.message_one.values[0]


def select_second_message(lesson):
    """Select the second message of a given lesson."""
    return lesson.message_two.values[0]


def prepare_tweet(day_two=False, spanish=False):
    """Prepare the tweet for tweeting. Workflow:
    * Get the google spreadsheet and dataframe from an authorized account.
    * Remove the last tweet's marker.
    * If this is the second day of the week, look for the previous tweet
        and send out the second message for that lesson.
    * If not, it's the first day of the week. So select a lesson at random
        and its associated link.
    * Update the queue based on what is about to be tweeted.
    * Return a string for the tweet consisting of the message and the link.
    """
    sheet, options_frame = get_tweet_contents_from_google(spanish)
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
    """Parses the command line for arguments.
    Two different potential arguments. One indicates if it is the
    second tweet of the day (assumes that is not the case). Another marks
    whether we should be tweeting Spanish (not implemented yet).
    """
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
    """Tweet a lesson."""

    # Get the arguments and prepare the tweet contents.
    args = parse_args()
    tweet_contents = prepare_tweet(args.day_two, args.spanish)

    # Try to tweet. If it works, log the success. If it doesn't, log the stack
    # trace for debugging later.
    try:
        tweet(tweet_contents)
        print('Success: ' + tweet_contents)
    except:
        # catch in the logs on heroku
        print('Fail: ' + tweet_contents + '\n')
        print(traceback.format_exc())
        with open('errors.txt', 'a') as fn:
            # catch in the logs locally.
            fn.write('===========')
            fn.write('Fail: ' + tweet_contents + '\n')
            fn.write(traceback.format_exc() + '\n')
            fn.write('===========' + '\n')
    rest(600)


if __name__ == '__main__':
    main()
