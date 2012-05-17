# Tweetscape function library
# (c) Yuri Yuan, 2012
# Last modification: 17 May 2012
# Working draft


import urllib
import httplib
import sys
import json as json
from urlparse import urlparse
import ConfigParser
import MySQLdb

def JsonGET(url, parameters = {}, retry_count = 5, retry_errors = None, retry_delay = 1):
    # Retrieve and decode JSON response from a REST API
    if len(parameters):
        url = '%s?%s' % (url, urllib.urlencode(parameters))
    # Need to add a caching mechanism
    
    # Determine whether a secured connection is used.
    if url[4] == 's':
        secure = True
    else:
        secure = False
    
    # Try to open the connection
    host = urlparse(url).netloc

    retries_performed = 0
    while retries_performed < retry_count + 1:
        if secure:
            conn = httplib.HTTPSConnection(host)
        else:
            conn = httplib.HTTPConnection(host)

    # Execute request
        try:
            conn.request('GET', url)
            resp = conn.getresponse()
        except Exception, e:
#            raise TweepError('Failed to send request: %s' % e)
            print 'sian'
            sys.exit(11)   # VET THE CODE HERE!

        # Exit request loop if non-retry error code
        if retry_errors:
            if resp.status not in retry_errors: break
        else:
            if resp.status == 200: break

        # Sleep before retrying request again
        time.sleep(retry_delay)
        retries_performed += 1
        
    result = json.loads(resp.read())
    conn.close()
        
        
        # FIXME: Put the result into cache
        
        
    return result

class Config:
    def __init__(self,file):
        self.file = file or 'default.conf'
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.file)
    
    def get(self,section,option):
        return self.config.get(section,option)
        
        
        

class Geocode:
    def __init__(self,db_cursor= None,yahoo_app_id=None):
        if db_connection is None or yahoo_app_id is None:
            pass # Supposed to throw an exception.
        self.db_cursor = db_cursor
        self.yahoo_app_id = yahoo_app_id
        
    def cache_write(self,name,lon,lat,radius,no_result):
        if no_result:
            query = "INSERT INTO geocodes (name,no_result) VALUES (%s,1);"
            query_param = (name)
        else:
            query = "INSERT INTO geocodes (name,lon,lat,radius) VALUES (%s,%s,%s,%s);"
            query_param = (name,lon,lat,radius)
        try:
            self.db_cursor.execute(query,query_param)
        except MySQLdb.IntegrityError:
            print 'Duplicate Entry In DB'
            
    def cache_read(self,name):        
        query = "SELECT * FROM geocodes WHERE name = '%s';"%(name,)
        if not self.db_cursor.execute(query):
            return false
        result = self.db_cursor.fetchone()
        if result[4]: # If no result was returned by the Geocoding API
            return {'no_result':True}
        else:
            return {'no_result':False,'lon':result[1],'lat':result[2],'radius':result[3]}
        
    def yahoo_query(self,name):
        url='http://where.yahooapis.com/geocode'
        parameters={'flags':'J'}
        name = urllib.quote_plus(name) # Encode name into Query String format
        parameters['location'] = name
        if self.yahoo_app_id:
            parameters['appid']=self.yahoo_app_id
        result = JsonGET(url,parameters)
        if (not result) or int(result['ResultSet']['Error']):
            return False
        if not int(result['ResultSet']['Found']):
            # Cache the result first
            cache_write(name,0,0,0,True)
            return {'no_result':True}
        result = result['ResultSet']['Results'][0]
        lon = float(result['longitude'])
        lat = float(result['latitude'])
        radius = int(result['radius'])
        cache_write(name,lon,lat,radius,False)
        return {'no_result':False,'lon':lon,'lat':lat,'radius':radius}
        