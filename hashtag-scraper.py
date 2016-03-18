import json
import twitter

with open('settings.json') as f_settings:
    settings = json.load(f_settings)

connection = twitter.Api(consumer_key=settings['app_key'],
                         consumer_secret=settings['app_secret'],
                         access_token_key=settings['token'],
                         access_token_secret=settings['token_secret'])

# Let's check if we really have some valid credentials
connection.VerifyCredentials()

tweets = connection.GetStreamSample()
words = set([])

for tweet in tweets:
    # Do we have to dump the collected dumps?
    if len(words) >= 100:
        with open('wordlist_hashtag', 'a') as f_wordlist:
            f_wordlist.write('\n'.join(words) + '\n')
        words = set([])

    # Skip non english tweets
    try:
        language = tweet['lang']
    except KeyError:
        continue

    if language != 'en':
        continue

    # If we don't have an hashtag, let's skip the tweet
    try:
        hashtags = tweet['entities']['hashtags']
    except KeyError:
        continue

    for hashtag in hashtags:
        text = hashtag['text']
        # We're interested in words of 10 chars at least
        if len(text) < 10:
            continue

        words.add(text)
