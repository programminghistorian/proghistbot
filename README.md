# Read Me

This repository collects the code used for the Twitter bot put together for [The Programming Historian](programminghistorian.org) by @walshbr. 

## Tweeting Process

Data is served out of a [Google spreadsheet](https://docs.google.com/spreadsheets/d/1o-C-3WwfcEYWipIFb112tkuM-XOI8pVVpA9_sag9Ph8/edit#gid=1625380994).

As of May 2017, the tweets are scheduled to go out the following days/times each week:

* Monday - 9AM PST, 12PM EST, 4PM London time
* Thursday 6:30 AM PST, 9:30 AM EST, 1:30PM London

The Thursday tweets are an ICYMI of Monday's content, reworded and often a bit more technical in nature. Each week the bot picks a random tweet from the spreadsheet. It will cycle through all the tweets until they're done, at which point it will start over again. So with one week per lesson we're looking at a year's worth of tweets. 

From a more technical point of view, the bot is a Python script that runs certain days of the week on Heroku. 

## Deploying
To deploy this yourself, you'll need a few things, depending on what you're trying to do:

* Write access to the Google spreadsheet.
* Write access to the Heroku remote, which can be granted by email.
* A JSON key that enables us to use the Google spreadsheet API. This can be shared by email.

It's important that we not commit sensitive data to the GitHub repository. The Twitter Credentials are all held in Environment variables in Heroku, but the Google spreadsheet JSON key is a bit more wonky. I've set it up so that the master branch points to GitHub while a separate branch, heroku, points to the heroku remote that deploys the remote. The heroku branch will never be committed to GitHub. The JSON key will never be committed to the master branch, so any future work will be to the master branch. When we merge into the heroku branch, our changes will be added without overwriting the heroku branch.  

For that reason, the general workflow to modify the bot is this. First clone the bot down and make your heroku branch:

```bash
$ git clone git@github.com:walshbr/proghistbot.git
$ git branch heroku
$ git checkout heroku
```

Then, add the JSON key (should be shared by email) to the repository and push it up to Heroku remote.

```bash
$ git add 'Programming_Historian-aa456f0a6b33.json'
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
$ git push heroku heroku:master
```
