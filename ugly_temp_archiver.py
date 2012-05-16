import tweepy
import json
import re
from MySQLdb import IntegrityError
from ssl import SSLError

import MySQLdb as mysql
import config
import re

db=mysql.connect(config.db_host,config.db_user,config.db_password,config.db_database)
cursor=db.cursor()

auth1 = tweepy.OAuthHandler('vSfPqwPbDpKSzOvcpIs3dg','fLvAmi0ATSgh8tHBTpo43VoFt2CivrVy5ayowDgg2g')
auth1.set_access_token('18546532-TsMqawKJHZt4C7Y3OUFBxdd6XyaeV7ShveDAokfki','r7yZOhjNc2PnGK3vkzBK48Va2Wsfe6sHRJEYtunGBxY')
api = tweepy.API(auth1);
user_credentials=api.verify_credentials();
print 'Twitter ID = ',user_credentials.id

#api.update_status('HiruKyoulyu, testing.')

class StreamListener(tweepy.StreamListener):
    """
    def on_data(self,data):
        print data
        print "\n\n"
    """
    print 'Starting...'
    def on_data(self, data):
        """Called when raw data is received from connection.

        Override this method if you wish to manually handle
        the stream data. Return False to stop stream and close connection.
        """
        if 'in_reply_to_status_id' in data:
            status = tweepy.Status.parse(self.api, json.loads(data))
            if self.on_status(status,data) is False:
                return False
        elif 'delete' in data:
            delete = json.loads(data)['delete']['status']
            if self.on_delete(delete['id'], delete['user_id']) is False:
                return False
        elif 'limit' in data:
            if self.on_limit(json.loads(data)['limit']['track']) is False:
                return False
    
	
    def on_status (self,status,data):
#        data = data.replace('"protected": true,','"protected": false,')
	query = "INSERT INTO raw_tweets (id,json) VALUES (%s,%s);"
	query_param = (int(status.id),data)
	try:
	    cursor.execute(query,query_param)
	except IntegrityError:
	    print 'Duplicate Entry In DB'
	print 'Incoming tweet: #%d @%s:'%(status.id,status.user.screen_name)
#	print status.text.encode('utf-8')  
#	print "."
listener1 = StreamListener();
streamer = tweepy.Stream(auth=auth1,listener=listener1,timeout=60)
def fetchstream():
    try:
        streamer.sample();
    except SSLError:
	print 'SSLError occurred. Reconnecting.'
#        fetchstream();
    

fetchstream();

