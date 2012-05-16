# Tweetscape archiver
# (c) Yuri Yuan, 2012
# Last modification: 25 April 2012

import sys # Used for non-zero exit codes

# Debug codes
archiver_file = "archiver.conf"


# Set crucial variables to None in case they are not properly defined in the argument
ConsumerKey = None
ConsumerSecret = None
AccessToken = None
AccessTokenSecret = None
db_Host = None
db_Username = None
db_Password = None
db_Database = None

# Process command line arguments at start
"""
import argparse

parser = argparse.ArgumentParser(description="Archive Tweets in the public timeline from the streaming API.")
parser.add_argument('-f','--config',default='archiver.conf', metavar='CONF_FILE',
                    help='Specify confiugration file to be loaded, default = archiver.conf')
parser.add_argument('-u','--unit-test', metavar='MODE',
                    help='Unit test mode. Options: no-db, ')
parser.add_argument('--consumer-key', metavar='KEY',
                    help='Consumer Key for Twitter API')
parser.add_argument('--consumer-key-secret', metavar='SECRET',
                    help='Consumer Key Secret for Twitter API')
parser.add_argument('--access_token', metavar='TOKEN',
                    help="Access Token for Twitter API")
parser.add_argument('--access_token_secret', metavar='SECRET',
                    help='Access Token Secret for Twitter API')
parser.add_adgument('-l','--log', metavar='LOG_FILE',
                    help='Specify log file')
parser.add_argument('-v','--verbose',)
parser.add_argument('-d','--daemon',)
"""

# Open the configuration file

import ConfigParser
config = ConfigParser.ConfigParser()
config.read(archiver_file)

# Initialise Tweepy

import tweepy
import simplejson as json
import ssl # The error classes are imported for exception handling.
try:
    if ConsumerKey is None:
        ConsumerKey = config.get('API Tokens','ConsumerKey')
    if ConsumerSecret is None:
        ConsumerSecret = config.get('API Tokens','ConsumerSecret')
    if AccessToken is None:
        AccessToken = config.get('API Tokens','AccessToken')
    if AccessTokenSecret is None:
        AccessTokenSecret = config.get('API Tokens','AccessTokenSecret')
except ConfigParser.NoOptionError, ConfigParser.NoSectionError:
    print 'You sure your config file valid or not? Like dat cannot connect to Twitter!'
    sys.exit(10) # Exit code 10: Necessary configurations not set

auth = tweepy.OAuthHandler(ConsumerKey,ConsumerSecret)
auth.set_access_token(AccessToken,AccessTokenSecret)
api = tweepy.API(auth);

# Initialise Database Connection
try:
    import MySQLdb
except ImportError:
    print "Your com MySQLdb library oso dun have ah? Like dat how?!"
    sys.exit(9) # Exit code 9: Failed to load required libraries

try:
    if db_Host is None:
        db_Host = config.get('Database','Host')
    if db_Username is None:
        db_Username = config.get('Database','Username')
    if db_Password is None:
        db_Password = config.get('Database','Password')
    if db_Database is None:
        db_Database = config.get('Database','Database')
except ConfigParser.NoOptionError, ConfigParser.NoSectionError:
    print 'You sure your config file valid or not? Like dat cannot connect to database!'
    sys.exit(10) # Exit code 10: Necessary configurations not set
    
db=MySQLdb.connect(db_Host, db_Username, db_Password, db_Database)
cursor=db.cursor()

# StreamListener class(es) to process the data returned from Twitter

class StreamListener_RecordJSON(tweepy.StreamListener):
    """
    The StreamListener classes that record JSON-formatted statuses.
    """
    print 'Starting...'
    
    def __init__ (self, monitor):
        """
        The monitor object is passed to StreamListener to enable process monitoring.
        """
        self.monitor = monitor
	self.api = tweepy.API()
    def on_data(self, data):
        """
        The original on_data method is overridden to pass the json data to the on_status method.
        """
        if 'in_reply_to_status_id' in data:
            status = tweepy.Status.parse(self.api, json.loads(data))
            if self.on_status(status,data) is False:
                return False

    def on_status (self,status,data):
        query = "INSERT INTO raw_tweets (id,json) VALUES (%s,%s);"
        query_param = (int(status.id),data)
        self.monitor.new_tweet(int(status.id))
        try:
            cursor.execute(query,query_param)
        except MySQLdb.IntegrityError: # Duplicate statuses may exist in the stream returned by Twitter, resulting in duplicate entries in database.
            pass
 
# Monitor class to monitor the spidering process

class MonitorClass:
    tweet_count = 0
    def new_tweet(self,id):
        if self.tweet_count == 0:
            print ('yep, there\'s a new tweet.\n')
        else:
            print 'New tweet: %d'%id
        self.tweet_count+=1
    

# Putting pieces together (for now)

monitor = MonitorClass()

listener = StreamListener_RecordJSON(monitor);
streamer = tweepy.Stream(auth=auth,listener=listener,timeout=60)

while 1:
    try:
        streamer.sample()
    except ssl.SSLError:
        pass
