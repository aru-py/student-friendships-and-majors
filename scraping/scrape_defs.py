from contextlib import suppress
from urllib.error import URLError
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
from requests import RequestException
import regex as re
from data_collection.exceptions import *
# from exceptions import *


def get_clemson_data(session, person):
    try:
        data = session.get("https://my.clemson.edu/srv/feed/dynamic/directory/search?name=" + person.name)
        person.cuid = data.json()[0].get('cn')
        data = session.get('https://my.clemson.edu/srv/feed/dynamic/directory/getInfoByCN?cn=' + person.cuid)
        data = data.json()
        if person.name.split() != [data.get('name').get('first'), data.get('name').get('last')]:
            raise PersonNotAtClemson(person)
    except (KeyError, IndexError, AttributeError, URLError):
        raise PersonNotAtClemson(person)
    else:
        try:
            person.class_standing = data.get('student').get('class')
            person.major = data.get('student').get('major').get('name')
            with suppress(Exception):
                urlretrieve(data['photo_url'], 'output/images/' + person.cuid + '.png')
        except AttributeError:
            pass


def get_venmo_data(session, person, proxy='http://77.83.87.14:8085'):
    try:
        data = session.get("https://venmo.com/" + person.username, timeout=2, proxies={'https': proxy})
        soup = BeautifulSoup(data.text, 'lxml')
        person.friends = [friend['details'].strip(')').split(' (') for friend in soup(cardtype='profile')]
        if not person.friends:
            raise TooManyRequests if 'Sorry' in data.text else SessionTimeOut

        rgx = re.compile(r"^venmo.page_user.*?id\":\s([0-9]*)", flags=re.MULTILINE)
        person.id = re.search(rgx, data.text).group(1)
        data = session.get("https://venmo.com/api/v5/users/" + person.id + "/feed", timeout=2, proxies={'https':proxy})
        data = data.json()

        person.transactions = [
            [t['actor']['username'], t['transactions'][0]['target']['username'], t['message'], t['created_time']]
            for t in data['data']]
    except RequestException:
        raise NonFatalException(person)

