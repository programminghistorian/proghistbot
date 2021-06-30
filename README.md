# Read Me

This repository collects the code used for the Twitter bot put together for [The Programming Historian](programminghistorian.org) by @walshbr.

## Tweeting Process

Data is served out of a [Google spreadsheet](https://docs.google.com/spreadsheets/d/1o-C-3WwfcEYWipIFb112tkuM-XOI8pVVpA9_sag9Ph8/edit#gid=1625380994).

You'll want to only add data to the id, message_one, message_two, and link columns. The tweet_log is managed by the bot itself to track its progress through the corpus of lessons.

Note: the ID column will probably be deprecated once I figure out a Pandas issue I was working through.

As of May 2017, the tweets are scheduled to go out the following days/times each week:

* Monday - 9AM PST, 12PM EST, 4PM London time
* Thursday 6:30 AM PST, 9:30 AM EST, 1:30PM London

The Thursday tweets are an ICYMI of Monday's content, reworded and often a bit more technical in nature. Each week the bot picks a random tweet from the spreadsheet. It will cycle through all the tweets until they're done, at which point it will start over again. So with one week per lesson we're looking at a year's worth of tweets.

## Heroku

From a more technical point of view, the bot is a Python script that runs certain days of the week on Heroku. The bot is called "proghistbot" on Heroku. As of right now, @walshbr owns the bot, and @mdlincoln, and @jerielizabeth are collaborators. If new people need to be added to the bot, contact @walshbr.

Heroku only allows workers to run every 10 minutes, hourly, or daily. So we get around this by having two workers scheduled to each go off once a day. When they fire, they check to see what day it is. If it's not a day of the week when their particular worker is scheduled to go off, they pass. So we're filtering to only run Monday/Thursday. You can check the behaviors for these scheduled tasks by clicking on "Resources" from the dashboard for the proghistbot app when logged into Heroku. This resource is called "Heroku Scheduler." I've also included a task that allows you to run a tweet immediately for testing purposes. Under "Resources" from the app dashboard, the worker "python bot.py" is by default off. Turning this worker on by clicking the pencil at right will have the bot run a tweet immediately.

Heroku logs can be viewed live from the terminal by running

```
$ heroku logs -t
```

Or, you can work locally by running:

```
$ heroku local
```

This will run the app locally using the procfile. In order to do so, however, you will need to store the Twitter credentials for the bot locally in a .env file. I've provided a template file, "template.env", that you can rename to ".env" - just place the bot credentials with the quotation marks. All Twitter credentials are stored as config variables in Heroku. You access them from the dashboard of the proghistbot app on Heroku by clicking on "Settings" > "Config Vars". These are linked to the Programming Historian's Twitter account, so they shouldn't ever need to be changed.

## Deploying and Development

To deploy this yourself, you'll need a few things, depending on what you're trying to do:

* Write access to the Google spreadsheet.
* Write access to the Heroku remote, which can be granted by email.
* A JSON key that enables us to use the Google spreadsheet API. This can be shared by email.

It's important that we not commit sensitive data to the GitHub repository. The Twitter Credentials are all held in Environment variables in Heroku, but the Google spreadsheet JSON key is a bit more wonky. I've set it up so that the master branch points to GitHub while a separate branch, heroku, points to the heroku remote that deploys the remote. The heroku branch will never be committed to GitHub. The JSON key will never be committed to the master branch, so any future work will be to the master branch. When we merge into the heroku branch, our changes will be added without overwriting the heroku branch.  

For that reason, the general workflow to modify the bot is this. First clone the bot down and make your heroku branch:

```bash
$ git clone https://github.com/programminghistorian/proghistbot.git
$ git branch heroku
$ git checkout heroku
```

Then, add the JSON key (should be shared by email) to the repository and push it up to Heroku remote.

```bash
$ git add 'proghist-google-credentials.json'
$ git add 'Setting up access to the Heroku remote.'
$ git push heroku heroku:master
```

From then on out you'll work on the master branch, merge into heroku, and push up your changes to the heroku branch.

```bash
$ git checkout master
[edit some files]
$ git add .
$ git commit -m 'Share a helpful message.'
$ git push origin master.
```

When ready to deploy to the heroku remote itself, you'll merge into the heroku branch.

```bash
$ git checkout heroku
$ git merge master
$ git push --force heroku heroku:master
```
Note: I added the --force flag because of our weird setup. Since we're using a sort of weird workflow it kept yelling at me that not all refs were shared.

When in doubt, you can always run
```bash
$ heroku run bash
```

to make sure that you haven't accidentally deleted the JSON key from the Heroku remote.

## Adding a new tweet routine

There are a few steps to adding a new routine to the bot.

1. Add a new spreadsheet tab to the spreadsheet linked above and populate the columns with a handful of tweets.
2. Work with the bot.py file to add the new category of tweets to your workflow. (see "Deploying and Development" above.)
3. Log into the heroku account and add the new tweet routines to the bot. [note from Brandon to himself: if there is no other info here it means I forgot to document this part and should be pinged!]

## Generating the JSON Keychain

In the event that we need to generate a fresh copy of the JSON key for whatever reason, you can do so from from the [Google Cloud Console](https://console.cloud.google.com/). After logging in, select the "Programming Historian" project, which might be variously referred to by its autogenerated name - rare-chiller-166520. To generate the Keychain, follow the steps documented by the [gspread library that we use for tweeting](http://gspread.readthedocs.io/en/latest/oauth2.html). You'll need to change the filename to 'proghist-google-credentials.json' and then follow the steps above.
