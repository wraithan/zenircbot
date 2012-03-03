from datetime import datetime, timedelta
from time import sleep
import re

from BeautifulSoup import BeautifulSoup
from feedparser import parse
from lib import api


api.register_commands('jira_feed.py', [])
jira_config = api.load_config("./jira.json")
jira_url = '%sbrowse/\\1' % jira_config['jira_url']
latest = None


def strtodt(string):
    return datetime.strptime(string, '%Y-%m-%dT%H:%M:%SZ')


while True:
    feed = parse(jira_config['feed_url'])
    if latest is None:
        latest = strtodt(feed['entries'][0].updated) - timedelta(seconds=1)
    entries = [entry for entry in feed['entries']
               if strtodt(entry.updated) > latest]
    for entry in entries:
        if strtodt(entry.updated) > latest:
            latest = strtodt(entry.updated)
        bs = BeautifulSoup(entry.title)
        message = ''.join(bs.findAll(text=True))
        if not ('created' in message or
                'resolved' in message or
                'reopened' in message):
            continue
        api.send_privmsg(jira_config['channel'],
                         'JIRA - %s' % re.sub('(\w\w-\d+)',
                                              jira_url,
                                              message))

    sleep(jira_config['poll_rate'])
