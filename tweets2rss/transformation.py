# For generating nice looking HTML content for each entry
from jinja2 import Template

def decorate(tweet, use_html=True):
    text = tweet['full_text']

    text_replacements = []

    if use_html:
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
        if use_html:
            replacement_template = Template('<a href="{{href}}">{{display_url}}</a>')
            replacement = replacement_template.render(href=expanded_url, display_url=display_url)
        else:
            replacement = display_url
        text_replacements.append({'start':start, 'end':end, 'replacement':replacement})

    # Remove all media urls (if any)
    if 'media' in tweet['entities']:
        media = tweet['entities']['media']
        for entry in media:
            indices = entry['indices']
            start = indices[0]
            end = indices[1]
            text_replacements.append({'start':start, 'end':end, 'replacement':''})

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
