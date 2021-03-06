"""`main` is the top level module for your Flask application."""

import env

# For generating RSS feed
from feedgen.feed import FeedGenerator

# For generating nice looking HTML content for each entry
from jinja2 import Template

# Import the Twitter library
from twitter import *

# Import the Flask Framework
from flask import Flask, request, make_response
app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

from tweets2rss.transformation import decorate

def get_media(tweet):
    if 'media' not in tweet['entities']:
        return ""

    concat = []
    media = tweet['entities']['media']
    for m in media:
        media_url = m['media_url']
        template = Template('<br><img src="{{media_url}}">')
        concat.append(template.render(media_url=media_url))

    return "".join(concat)

def get_feed(feed_title, feed_description, feed_link, tweets, screen_name_in_title=False):
    fg = FeedGenerator()

    fg.title(feed_title)
    fg.description(feed_description)
    fg.link(href=feed_link)
    fg.image('https://abs.twimg.com/favicons/favicon.ico')

    for tweet in tweets:
        fe = fg.add_entry()
        fe.id(tweet['id_str'])
        screen_name = tweet['user']['screen_name']

        title = decorate(tweet, use_html=False)

        if screen_name_in_title:
            fe.title('@' + screen_name + ': ' + title)
        else:
            fe.title(title)

        fe.link(href='https://twitter.com/%s/status/%s' % (screen_name, tweet['id_str']))
        fe.published(tweet['created_at'])

        text = decorate(tweet)
        media = get_media(tweet)

        profile_image = tweet['user']['profile_image_url']
        name = tweet['user']['name']

        template = Template("""
            <html>
                <style>
                a {
                    text-decoration: none;
                }
                </style>
                <body>
                    <table>
                    <tr>
                        <td><img src="{{profile_image}}"></td>
                        <td>
                            <strong>{{name}}</strong><br>
                            @{{screen_name}}
                        </td>
                    </tr>
                    </table>
                    <br>
                    {{text}}
                    {{media}}
                </body>
            </html>
        """)
        fe.content(template.render(text=text, media=media, profile_image=profile_image, name=name, screen_name=screen_name))

    return fg.rss_str(pretty=True) # Get the RSS feed as string

@app.route('/user')
def parse_user():
    """Parses a Twitter user's tweets and return a corresponding RSS feed."""

    password = request.args.get('password')
    if password != env.PASSWORD:
        return 'Unauthorized', 401

    t = Twitter(auth=OAuth(env.ACCESS_TOKEN, env.ACCESS_TOKEN_SECRET, env.CONSUMER_KEY, env.CONSUMER_SECRET))

    screen_name = request.args.get('screen_name')
    if screen_name == None:
        return 'No screen_name provided', 500

    include_rts = True
    if request.args.get('no_rt') == 'true':
        include_rts = False

    exclude_replies = False
    if request.args.get('no_replies') == 'true':
        exclude_replies = True

    tweets = t.statuses.user_timeline(screen_name=screen_name,
                                      include_rts=include_rts,
                                      exclude_replies=exclude_replies,
                                      tweet_mode='extended')

    feed_title = screen_name
    feed_description = screen_name + "'s tweets"
    if len(tweets) > 0:
        feed_title = tweets[0]['user']['name'] + ' on Twitter'
        if len(tweets[0]['user']['description']) > 0:
            feed_description = tweets[0]['user']['description']

    feed_link = 'https://twitter.com/' + screen_name

    return get_feed(feed_title, feed_description, feed_link, tweets)


@app.route('/list')
def parse_list():
    """Parses a Twitter list and return a corresponding RSS feed."""

    password = request.args.get('password')
    if password != env.PASSWORD:
        return 'Unauthorized', 401

    t = Twitter(auth=OAuth(env.ACCESS_TOKEN, env.ACCESS_TOKEN_SECRET, env.CONSUMER_KEY, env.CONSUMER_SECRET))

    slug = request.args.get('slug')
    if slug == None:
        return 'No slug provided', 500

    screen_name = request.args.get('screen_name')
    if screen_name == None:
        return 'No screen_name provided', 500

    include_rts = True
    if request.args.get('no_rt') == 'true':
        include_rts = False

    list_info = t.lists.show(owner_screen_name=screen_name, slug=slug)

    tweets = t.lists.statuses(owner_screen_name=screen_name,
                              slug=slug,
                              include_rts=include_rts,
                              count=200,
                              tweet_mode='extended')

    feed_title = '@' + list_info['user']['screen_name'] + '/' + list_info['name'] + ' on Twitter'
    feed_description = 'A list by ' + list_info['user']['name']
    if len(list_info['description']) > 0:
        feed_description = list_info['description']

    feed_link = 'https://twitter.com/%s/lists/%s' % (screen_name, slug)

    return get_feed(feed_title, feed_description, feed_link, tweets, True)


@app.route('/search')
def parse_search():
    """Parses a Twitter search query and return a corresponding RSS feed."""
    return 'Hello Search!'


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500
