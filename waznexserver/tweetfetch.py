import datetime
import simplejson as json
import requests
import re
import urllib
import tempfile
import os

from waznexserver import app
from waznexserver import db
import models
from sqlalchemy import desc

url_regex = re.compile(r'http[^ ]+')
twitter_search_phrase = 'bcgr-talks'

def go(last_url=None):
    'returns (filename, url) if new image found, else None'
    # Get the last fetched image
    last_tfi = db.session.query(models.TweetFetchImage).\
               order_by(desc('fetch_dt')).first()
    if last_tfi:
        last_url = last_tfi.url
    else:
        last_url = None
    # Fetch the most current image, or None if it's the same as the last one
    (img, url) = get_picture(last_url)
    if img is None:
        return None
    #print img
    #print url
    fetch_ts = datetime.datetime.utcnow() - datetime.timedelta(hours=4)
    filename = ('%sFtweetimg.jpg') %\
                       (fetch_ts.strftime(app.config['FILE_NAME_DT_FORMAT']),)
    filepath = os.path.join(app.config['IMAGE_FOLDER'], filename)
    fd = os.open(filepath, os.O_RDWR|os.O_CREAT)
    f = os.fdopen(fd, 'w')
    f.write(img)
    f.close()
    # Initialize GridItem and add it to the list
    grid_item = models.GridItem(fetch_ts, filename)
    db.session.add(grid_item)
    grid_item.status = models.IMAGESTATUS_NEW
    # Initialize URL and add it to the DB
    tfi = models.TweetFetchImage(fetch_ts, url)
    db.session.add(tfi)
    db.session.commit()
    app.logger.info('Adding image: ' + filename)
    #print 'saved to %s' % filepath
    return url

def get_picture(last_orig_url):
    twitter_search = requests.get('http://search.twitter.com/search.json?q=%s&result_type=recent&count=5' % urllib.quote(twitter_search_phrase))
    tweets = json.loads(twitter_search.content)
    for tweet in tweets['results']:
        #print tweet['text']
        match = url_regex.search(tweet['text'])
        if match:
            tweet_url = match.group(0)
            if tweet_url == last_orig_url:
                #print 'first match is the same as last time %s' % tweet_url
                return None, tweet_url
            embed_url = 'http://api.embed.ly/1/oembed?url=%s&format=json' % urllib.quote(tweet_url)
            embed_response = requests.get(embed_url)
            if embed_response.status_code == 200:
                embed = json.loads(embed_response.content)
                if embed['type'] == 'photo':
                    image_response = requests.get(embed['url'])
                    if image_response.status_code == 200:
                        return image_response.content, tweet_url
                else:
                    print embed
            else:
                print 'could not find raw img url for %s' % response.url
        else:
            print 'regex did not match'
    return None, None

if __name__ == '__main__':
    go()
