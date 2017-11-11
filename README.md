# tweets2rss

Generates RSS feeds from Twitter.

E.g.
Generating a RSS feed from Twitter list:  
`https://project_name.appspot.com/list?password=secret&screen_name=twitter_handle&slug=twitter_list_slug`

## Development & Deployment
This project is designed to be deployed to Google App Engine (GAE). For a single person's usage, the GAE free tier should be sufficient.

Google's instruction on how to deploy to App Engine is [here][1].

First, you want to create an isolated Python environment using `virtualenv`:
```
virtualenv venv
source venv/bin/activvat
```

Install dependencies. This step is necessary since GAE deployment will upload the files from the libraries too.
```
pip install -t lib -r requirements.txt
```

Create a `env.py` file. This is for configuring your own deployment with your Twitter keys.
```
PASSWORD = "password to prevent random people from accessing the service"
CONSUMER_KEY = "get this from Twitter"
CONSUMER_SECRET = "get this from Twitter"
ACCESS_TOKEN = "get this from Twitter"
ACCESS_TOKEN_SECRET = "get this from Twitter"
```

To deploy:
```
gcloud app deploy --project=get_this_from_gae --version=some_version_you_track
```

  [1]: https://cloud.google.com/appengine/docs/standard/python/getting-started/python-standard-env
