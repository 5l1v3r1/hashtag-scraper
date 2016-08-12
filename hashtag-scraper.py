import argparse
import json
import twitter
import logging
import logging.handlers
from colorlog import ColoredFormatter
from datetime import date
from os import path as os_path
from lib.exceptions import exceptions
from requests.exceptions import ChunkedEncodingError
from socket import error as socket_error
from time import sleep


class HashtagScraper:
    def __init__(self):

        self.settings = None
        self.version = '1.0.1'
        self.language = 'en'

        # Let's parse some CLI options
        parser = argparse.ArgumentParser()
        parser.add_argument('-l', '--lang', help='Filter tweets by language', default='en')
        parser.add_argument('-e', '--length', help='Minimum length for the hashtag', default=10)

        arguments = parser.parse_args()

        self.language = arguments.lang
        self.length = arguments.length

        # Init the logger
        self.logger = logging.getLogger('hashtag-scraper')
        self.logger.setLevel(logging.DEBUG)

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)

        formatter = ColoredFormatter("%(log_color)s%(asctime)s|[%(levelname)-4s] %(message)s%(reset)s", "%H:%M:%S")
        console.setFormatter(formatter)
        self.logger.addHandler(console)

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

        words = set([])

        # I'll wrap everything inside a busy loop, so I can resume it if the connection fails.
        while True:
            self.logger.info("Request tweet stream...")

            tweets = connection.GetStreamSample()
            reported_length = 0

            self.logger.info("Got stream, starting to analyze tweets")

            try:
                for tweet in tweets:
                    # Do we have to dump the collected dumps?
                    if len(words) >= 500:
                        self.logger.info("Fetched more than 500 hashtags, dumping them to file")

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
                        if len(text) < self.length:
                            continue

                        try:
                            words.add(text.encode('utf-8').lower())

                            if len(words) % 100 == 0 and len(words) != reported_length:
                                reported_length = len(words)
                                self.logger.info("Fetched %s words" % str(len(words)))
                        except:
                            # If we get any encoding error, simply skip the hashtag
                            continue
            except (ChunkedEncodingError, socket_error):
                # This happens when we can't keep up with Twitter feed, they will close the connection
                self.logger.warn("Connection error, resuming...")
                sleep(2)
                continue
            except KeyboardInterrupt:
                # mhm something bad happened, let's dump the wordlist before dying
                self.logger.warn("Operation aborted")
                with open('wordlist_hashtag.txt', 'a') as f_wordlist:
                    f_wordlist.write('\n'.join(words) + '\n')
                break
            except:
                # mhm something bad happened, let's dump the wordlist before dying
                self.logger.warn("Unexpected error, dumping hashtags before dying")
                with open('wordlist_hashtag.txt', 'a') as f_wordlist:
                    f_wordlist.write('\n'.join(words) + '\n')
                break


try:
    scraper = HashtagScraper()
    scraper.run()
except KeyboardInterrupt:
    print("Operation aborted")
