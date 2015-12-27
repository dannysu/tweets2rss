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


def decorate_tweet_text(tweet):
    text = tweet['text']

    text_replacements = []

    # Replace hashtags with clickable links
    hashtags = tweet['entities']['hashtags']
    for hashtag in hashtags:
        indices = hashtag['indices']
        start = indices[0]
        end = indices[1]
        hashtag_text = hashtag['text']
        replacement_template = Template('<a href="https://twitter.com/hashtag/{{hashtag}}?src=hash">{{original_text}}</a>')
        replacement = replacement_template.render(hashtag=hashtag_text, original_text=text[start:end + 1])
        text_replacements.append({'start':start, 'end':end, 'replacement':replacement})

    # Replace user mentions with clickable links
    user_mentions = tweet['entities']['user_mentions']
    for mention in user_mentions:
        indices = mention['indices']
        start = indices[0]
        end = indices[1]
        user_id = mention['screen_name']
        replacement_template = Template('<a href="https://twitter.com/{{screen_name}}">{{original_text}}</a>')
        replacement = replacement_template.render(screen_name=user_id, original_text=text[start:end + 1])
        text_replacements.append({'start':start, 'end':end, 'replacement':replacement})

    # Replace urls with clickable links
    urls = tweet['entities']['urls']
    for url in urls:
        indices = url['indices']
        start = indices[0]
        end = indices[1]
        display_url = url['display_url']
        expanded_url = url['expanded_url']
        replacement_template = Template('<a href="{{href}}">{{display_url}}</a>')
        replacement = replacement_template.render(href=expanded_url, display_url=display_url)
        text_replacements.append({'start':start, 'end':end, 'replacement':replacement})

    text_replacements = sorted(text_replacements, key=lambda replacement: replacement['start'])

    text_components = []

    start = 0
    for replacement in text_replacements:
        if replacement['start'] - start > 0:
            text_components.append(text[start:replacement['start']])
        text_components.append(replacement['replacement'])
        start = replacement['end'] + 1

    if start < len(text) - 1:
        text_components.append(text[start:])

    return "".join(text_components)

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

    tweets = t.statuses.user_timeline(screen_name=screen_name, include_rts=include_rts, exclude_replies=exclude_replies)

    fg = FeedGenerator()

    feed_title = screen_name
    feed_description = screen_name + "'s tweets"
    if len(tweets) > 0:
        feed_title = tweets[0]['user']['name'] + ' on Twitter'
        if len(tweets[0]['user']['description']) > 0:
            feed_description = tweets[0]['user']['description']
        fg.image(tweets[0]['user']['profile_image_url'])

    fg.title(feed_title)
    fg.description(feed_description)
    fg.link(href='https://twitter.com/' + screen_name)

    for tweet in tweets:
        fe = fg.add_entry()
        fe.id(tweet['id_str'])
        fe.title(tweet['text'])
        fe.link(href='https://twitter.com/%s/status/%s' % (screen_name, tweet['id_str']))
        fe.published(tweet['created_at'])

        text = decorate_tweet_text(tweet)
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
