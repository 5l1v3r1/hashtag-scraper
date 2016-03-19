# Hashtag Scraper

Passwords are slowing transforming into passphrases: several words packed together.  
Bruteforcing them is not an option, since their length could easily be longer than 12 chars.  
The only option is to use a dictionary and start combining the words, however we could miss some "slang" words. The best way is to actually gather some real world phrases using Twitter hashtags.

### Requirements
First of all copy the file `settings-dist.json` to `settings.json`; we'll need it later to store some details.  

Then install the requirements using `pip`:  
`pip install -r requirements.txt`   

Finally, you'll have to create a [Twitter App](https://apps.twitter.com/); this is a required step otherwise you won't be able to connect to Twitter service. Once you get the the App credentials (*API key*, *API secret*, *Access Token* and *Access Token Secret*), copy them inside the `settings.json` file you copied before.

### Usage
`python hashtag-scraper.py [OPTIONS]`  

Fetched hashtags are dumped inside the `wordlist_hashtag.txt` file.

### Options
Hashtag Scraper has some options for fine tuning:

```
-l LANG   --lang   LANG     Filter tweets by language (default to 'en')
-e LENGTH --length LENGTH   Minimum length for the hashtag (default to 10)
```

### Bug report
Feel free to open an issue and, if confirmed, create a Pull Request!
