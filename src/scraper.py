"""
scraper.py

"""

import pickle
from multiprocessing import Manager
from multiprocessing import Pool
from multiprocessing import Queue
from multiprocessing import cpu_count
from time import sleep

import numpy as np
import pandas as pd
from requests import Session

from exceptions import *
from models import Person
from utilities import get_clemson_data
from utilities import get_venmo_data


def load_settings():
    sessions[0].headers.update({'Referer': 'https://my.clemson.edu/'})
    with open('settings/cookies.txt') as c, open('settings/proxies.txt') as p:
        [s.headers.update({k: v}) for s in sessions for k, v in map(lambda l: l[:-1].split(': ', 1), c.readlines())]
        global proxies
        proxies = [line[:-1] for line in p.readlines()]
        np.random.shuffle(proxies)


def load_state():
    with open('output/queue.pkl', 'rb') as f, open('output/directory.pkl', 'rb') as d:
        [q.put(person) for person in f]
        directory.update(pickle.load(d))


def initialize():
    test_people = [['Nayoung Kim', 'nana99'], ]
    [q.put(person) for person in test_people]


def save():
    pd.DataFrame(data).to_csv('output/out.csv')
    ret = []
    try:
        while not q.empty():
            ret.append(q.get(timeout=3))
    except Exception as e:
        print("Could not save queue.", e)
    with open('output/queue.pkl', 'wb') as f:
        pickle.dump(ret, f)
    with open('output/directory.pkl', 'wb') as f:
        pickle.dump(dict(directory), f)


sessions = [Session()] * 2

directory = Manager().dict()
q = Queue()

data = []
proxies = []

load_settings()
initialize()


# primary scraping method
def scrape(z):
    # noinspection PyBroadException
    # get person from queue
    try:
        person = Person(q.get(timeout=5))
    except Exception:
        return

    # select random proxy
    proxy = 'http://' + np.random.choice(proxies)

    try:
        if person.username in directory:
            raise PersonInDirectory(person)

        get_clemson_data(sessions[0], person)
        get_venmo_data(sessions[1], person, proxy=proxy)

    # Non-Fatal Exceptions arise when indiviuals do not need to be scraped
    except NonFatalException as e:
        if isinstance(e, PersonInDirectory):
            pass
        elif isinstance(e, PersonNotAtClemson):
            directory[person.username] = False

    # Fatal Exceptions are those that interrupt program flow
    except FatalException as e:
        if isinstance(e, TooManyRequests):
            pass
        # if session times out, program goes to sleep while settings update
        elif isinstance(e, SessionTimeOut):
            print("SLEEPING")
            sleep(900)
            load_settings()
        q.put([person.name, person.username])

    # catch unexpected exceptions
    except Exception as e:
        print("UNKNOWN ERROR", e)

    # add person to directory and friends to queue
    else:
        directory[person.username] = True
        [q.put(friend) for friend in person.friends]
        return person.dump()


# scraping loop
def run(n):
    print('Scraping started.')
    pool = Pool(cpu_count())
    # keep scraping until either queue is empty or goal is reached
    while not q.empty() and len(data) < n:
        data.extend(filter(None, pool.map(scrape, range(3000))))
        print("Number of people checked:{}".format(len(directory)))
        print("Number of students scraped:{}".format(len(data)))
        # save data at intervals
        with open('output/directory.pkl', 'wb') as f:
            pickle.dump(dict(directory), f)
        pd.DataFrame(data).to_csv('output/out.csv')
    pool.close()
    print('Scraping Finished')


run(30000)
save()

print("Number of people checked:{}".format(len(directory)))
print("Number of students scraped:{}".format(len(data)))
