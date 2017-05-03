# import secret
import os
import requests
from tweepy import OAuthHandler, API
import csv
import random
import re
import time

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


def tweet_image_from_url(url, message):
    """tweets with an image from a url. """
    api = twitter_api()
    filename = 'temp.jpg'
    request = requests.get(url, stream=True)
    if request.status_code == 200:
        with open(filename, 'wb') as image:
            for chunk in request:
                image.write(chunk)

        api.update_with_media(filename, status=message)
        os.remove(filename)
    else:
        print("Unable to download image")


def tweet_with_image_from_filename(message, filename):
    api = twitter_api()
    api.update_with_media(filename, status=message)


def get_tweet_contents(filename):
    """Reads in a csv from given filename. returns a list of dictionary
    items pertaining to each lesson."""
    results = []
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            results.append(row)
    return results


def select_random_lesson(lessons):
    """given a list of lessons, select one at random"""
    return random.choice(lessons)


def select_random_message(lesson):
    choice = random.choice(['message-one', 'message-two'])
    print(lesson)
    print(choice)
    return lesson[choice]


def prepare_tweet():
    options = get_tweet_contents('tweet-manifest.csv')
    lesson = select_random_lesson(options)
    message = select_random_message(lesson)
    link = lesson['lesson-link']
    image_link = 'gallery/' + re.sub(
        r'http://programminghistorian\.org/lessons/', '', link) + '.png'
    return message + link, image_link


def rest(max_sleep):
    time.sleep(random.random() * max_sleep)


def main():
    # /gallery/slug.png
    # so for a tweet you need, message, slug for link, filename.
    # messages will need to be distinct for each.
    # easiest would be a csv file in the format,
    # id, message, link, image link
    tweet_contents = prepare_tweet()
    try:
        tweet_with_image_from_filename(tweet_contents[0],
                                       tweet_contents[1])
        print('Success: ' + tweet_contents[0] + tweet_contents[1])
    except:
        print('Fail: ' + tweet_contents[0] + tweet_contents[1])


if __name__ == '__main__':
    main()
