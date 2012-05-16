# Tweetscape archiver
# (c) Yuri Yuan, 2012
# Last modification: 25 April 2012

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

# Read from configuration file


