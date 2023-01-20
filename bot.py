#! /usr/bin/env python3
# coding=utf-8

from __future__ import unicode_literals
import os
import sys
import argparse
from mastodon import Mastodon
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import traceback
import time

# To add a new tab there are several spots to edit, marked in the script below with TODO.

# n.b. Since this script was original written as a Twitter bot, it uses the word "tweet" throughout, even though now its posts/toots on Mastodon.

# For local testing you just run the script with regular arguments based on what language you're testing (note that you must have the Google credentials in a JSON on your local machine):
# $ python bot.py -es True -t True
# You'll also need to manually create a secret token for the Mastodon account you'd like to post to. Make sure you don't post it to Github!
# Github Actions will add separate arguments for the scheduling, but this should immediately send a tweet out from the ProgHist account (or offer the opportunity to debug).


def rest(max_sleep):
    """Rest after tweeting - used when testing. """
    time.sleep(random.random() * max_sleep)


def masto_api():
    """Initialize Mastodon API, authorize, and return a usable object."""
    mastodon = Mastodon(
        access_token = 'token.secret',
        api_base_url = 'https://hcommons.social/'
    )

    return mastodon


def tweet(message):
    """Tweets a prepared message using the authorized API."""
    print(message)
    mastodon = masto_api()
#    mastodon.status_post(message)

# TODO: Add a new tab here w/ "title=False"
def get_tweet_contents_from_google(spanish=False, french=False, communications=False, portuguese=False):
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
    if french:
        print('tweeting in french')
        list_of_items = wks.worksheet('French').get_all_values()
        headers = list_of_items.pop(0)
        return wks.worksheet('French'), pd.DataFrame(list_of_items, columns=headers)
    if communications:
        print('tweeting from the communications tab')
        list_of_items = wks.worksheet('Communications').get_all_values()
        headers = list_of_items.pop(0)
        return wks.worksheet('Communications'), pd.DataFrame(list_of_items, columns=headers)
    if portuguese:
        print('tweeting in Portuguese')
        list_of_items = wks.worksheet('Portuguese').get_all_values()
        headers = list_of_items.pop(0)
        return wks.worksheet('Portuguese'), pd.DataFrame(list_of_items, columns=headers)
    # TODO: add a new tab here
    # if NAME_OF_TAB:
    #     print('tweeting from the NAME_OF_TAB tab')
    #     list_of_items = wks.worksheet('NAME_OF_TAB').get_all_values()
    #     headers = list_of_items.pop(0)
    #     return wks.worksheet('NAME_OF_TAB'), pd.DataFrame(list_of_items, columns=headers)
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

    cell_label = 'D' + str(int(id_num.values[0]) + 2)
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
            cell_label = 'D' + str(index_num + 2)
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
    cell_label = 'D' + str(int(id_num) + 2)
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

# TODO: add a new tab here with "name=False"
def prepare_tweet(day_two=False, spanish=False, french=False, communications=False, portuguese=False):
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
    # TODO: add a new tab option by extending the parenthetical
    sheet, options_frame = get_tweet_contents_from_google(spanish, french, communications, portuguese)
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
    A few different potential arguments. One indicates if it is the
    second tweet of the day (assumes that is not the case). Another marks
    whether we should be tweeting in a particular language.
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
    parser.add_argument('-fr', '--french', dest='french', type=bool,
                        default=False,
                        help='Set tweets to be French. '
                        'Default = False')
    parser.add_argument('-co', '--communications', dest='communications', type=bool,
                    default=False,
                    help='Set tweets to be from the communications tab. '
                    'Default = False')
    parser.add_argument('-pt', '--portuguese', dest='portuguese', type=bool,
                    default=False,
                    help='Set tweets to be from the portuguese tab. '
                    'Default = False')    
    # TODO: add a new tab w/ template for adding new tabs
    # parser.add_argument('-co', '--communications', dest='communications', type=bool,
    #                 default=False,
    #                 help='Set tweets to be from the communications tab. '
    #                 'Default = False')    
    return parser.parse_args(argv)


def main():
    """Tweet a lesson."""

    # Get the arguments and prepare the tweet contents.
    args = parse_args()
    print('grabbing tweet contents')
    # TODO: add new tab here by adding a new args.NAME piece
    tweet_contents = prepare_tweet(args.day_two, args.spanish, args.french, args.communications, args.portuguese)
    print('tweet contents grabbed')
    # Try to tweet. If it works, log the success. If it doesn't, log the stack
    # trace for debugging later.
    try:
        print('trying to tweet')
        tweet(tweet_contents)
        print('Success: ' + tweet_contents)
    except:
        # catch in the logs
        print('Something went wrong')
        print('Fail: ' + tweet_contents)
        print(traceback.format_exc())
    #rest(600)


if __name__ == '__main__':
    main()
