# Programming Historian Mastodon Bot

This repository collects the code used for the Mastodon bot put together for [The Programming Historian](programminghistorian.org). Our Mastodon account cross-posts to Twitter, and this code is based on the original Twitter bot written by @walshbr. It was adapted to work with Mastodon and Github Actions by [John Ladd](https://github.com/jrladd).

## Adding a new post routine

There are a few steps to adding a new routine to the bot.

1. Add a new spreadsheet tab to the spreadsheet linked above and populate the columns with a handful of posts (see "Posting Process").
2. Work with the bot.py file to add the new category of posts to your workflow. (see "Deploying and Development".)
3. Add a new step to the Github Actions schedule at `.github/workflows/bot.yml`.

## Posting Process

Data is served out of a [Google spreadsheet](https://docs.google.com/spreadsheets/d/1o-C-3WwfcEYWipIFb112tkuM-XOI8pVVpA9_sag9Ph8/edit#gid=1625380994).

You'll want to only add data to the message_one, message_two, and link columns. The tweet_log is managed by the bot itself to track its progress through the corpus of lessons. _But_ when starting a spreadsheet for the first time you will want to have at least one XY value in the tweet_log column to start things off. 

As of January 2023, the posts are scheduled to go out the following days/times each week:

* English: Monday & Thursday, 5PM UTC
* Spanish: Tuesday & Friday, 5PM UTC
* French: Wednesday & Saturday, 5PM UTC
* Portuguese: Thursday 12PM UTC & Sunday 5PM UTC

The second day's posts for each language are an ICYMI of the first day's content, reworded and often a bit more technical in nature. Each week the bot picks a random post from the spreadsheet. It will cycle through all the posts until they're done, at which point it will start over again.

## Github Actions

From a more technical point of view, the bot is a Python script that runs certain days of the week using Github Actions. You can pause the bot at any time by going to the "Actions" tab on Github, selecting the "Proghist Mastodon Bot" action, clicking the ellipses button (`...`) at the right of the page, and selecting "Disable workflow." You can click "Enable workflow" whenever you're ready to restart.

This bot was made with the help of [this excellent tutorial](https://github.com/PhantomInsights/actions-bot), and it follows the Github Actions procedure for [scheduling multiple events](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule). If you need to add something to the `bot.yaml` schedule, you can follow those two guides to do so.

## Deploying and Development

To deploy this yourself, you'll need a few things, depending on what you're trying to do:

* Write access to the Google spreadsheet.
* Write access to the Heroku remote, which can be granted by email.
* A JSON key that enables us to use the Google spreadsheet API. This can be shared by email, or you can generate a new one for yourself.

It's important that we not commit sensitive data to the GitHub repository. The Mastodon and Google credentials are all held in Secrets section of this repo. If you need access to any of these credentials, you can reach out to a member of the Programming Historian team.

## Generating the JSON Keychain

In the event that we need to generate a fresh copy of the JSON key for whatever reason, you can do so from from the [Google Cloud Console](https://console.cloud.google.com/). To generate the Keychain, follow the steps documented by the [gspread library that we use for posting](http://gspread.readthedocs.io/en/latest/oauth2.html). You'll need to copy the contents of the resulting JSON file into the Secrets section of the bot's Github repo.
