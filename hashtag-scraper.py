import argparse
import json
import twitter
from datetime import date
from os import path as os_path
from lib.exceptions import exceptions


class HashtagsScraper:
    def __init__(self):

        self.settings = None
        self.version = '1.0.0'
        self.language = 'en'

        # Let's parse some CLI options
        parser = argparse.ArgumentParser()
        parser.add_argument('-l', '--lang', help='Filter tweets by language', default='en')

        arguments = parser.parse_args()

        if arguments.lang:
            self.language = arguments.lang

    def checkenv(self):
        if not os_path.exists(os_path.realpath("settings.json")):
            raise exceptions.InvalidSettings("Please rename the file settings-dist.json to settings.json and fill the required info")

        with open(os_path.realpath("settings.json")) as f_settings:
            settings = json.load(f_settings)

        required_keys = ['app_key', 'app_secret', 'token', 'token_secret']

        for required in required_keys:
            try:
                value = settings[required]

                if value == '':
                    raise exceptions.InvalidSettings("Please fill the required info '" + required + "' before continuing")

            except KeyError:
                raise exceptions.InvalidSettings("Please fill the required info '" + required + "' before continuing")

        self.settings = settings

    def banner(self):
        print("Hashtag Scraper " + self.version + " - A better way of scraping")
        print("Copyright (C) " + str(date.today().year) + " FabbricaBinaria - Davide Tampellini")
        print("===============================================================================")
        print("Dump Scraper is Free Software, distributed under the terms of the GNU General")
        print("Public License version 3 or, at your option, any later version.")
        print("This program comes with ABSOLUTELY NO WARRANTY as per sections 15 & 16 of the")
        print("license. See http://www.gnu.org/licenses/gpl-3.0.html for details.")
        print("===============================================================================")

    def run(self):
        self.banner()

        # Perform some sanity checks
        try:
            self.checkenv()
        except exceptions.InvalidSettings as error:
            print error
            return

        connection = twitter.Api(consumer_key=self.settings['app_key'],
                                 consumer_secret=self.settings['app_secret'],
                                 access_token_key=self.settings['token'],
                                 access_token_secret=self.settings['token_secret'])

        # Let's check if we really have some valid credentials
        connection.VerifyCredentials()

        print "Request tweet stream..."

        tweets = connection.GetStreamSample()
        words = set([])

        print "Got stream, starting to analyze tweets"

        for tweet in tweets:
            # Do we have to dump the collected dumps?
            if len(words) >= 500:
                print "Fetched more than 500 hashtags, dumping them to file"

                with open('wordlist_hashtag.txt', 'a') as f_wordlist:
                    f_wordlist.write('\n'.join(words) + '\n')
                words = set([])

            # Skip non english tweets
            try:
                language = tweet['lang']
            except KeyError:
                continue

            if language != self.language:
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

                try:
                    words.add(text.encode('utf-8').lower())
                except:
                    # If we get any encoding error, simply skip the hashtag
                    continue


try:
    scraper = HashtagsScraper()
    scraper.run()
except KeyboardInterrupt:
    print("Operation aborted")
