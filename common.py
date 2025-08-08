#!/usr/bin/env python
"""This module provides a function for shipping logs to Airtable."""
import os
import time
from pyairtable import Api
import tweepy

api = Api(os.environ['AIRTABLE_PAT'])

airtab_msleg = api.table(os.environ['msleg_db'], 'log')

airtab_agendas = api.table(os.environ['msleg_db'], 'cmte_agendas')

airtab_log = api.table(os.environ['log_db'], 'log')

def get_twitter_conn_v1(api_key, api_secret, access_token, access_token_secret) -> tweepy.API:
    """Get twitter conn 1.1"""
    auth = tweepy.OAuth1UserHandler(api_key, api_secret)
    auth.set_access_token(
        access_token,
        access_token_secret,
    )
    return tweepy.API(auth)

def get_twitter_conn_v2(api_key, api_secret, access_token, access_token_secret) -> tweepy.Client:
    """Get twitter conn 2.0"""
    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )
    return client

client_v1 = get_twitter_conn_v1(os.environ['TWITTER_APP_KEY'], os.environ['TWITTER_APP_SECRET'], os.environ['TWITTER_OAUTH_TOKEN'], os.environ['TWITTER_OAUTH_TOKEN_SECRET'])
client_v2 = get_twitter_conn_v2(os.environ['TWITTER_APP_KEY'], os.environ['TWITTER_APP_SECRET'], os.environ['TWITTER_OAUTH_TOKEN'], os.environ['TWITTER_OAUTH_TOKEN_SECRET'])


my_funcs = {'scrape_cmte_schedules': 'recJaBXtAv0IddOdI'}


def wrap_from_module(module):
    def wrap_it_up(t0, new=None, total=None, function=None):
        this_dict = {
            'module': module,
            'function': function,
            '_function': my_funcs[function],
            'duration': round(time.time() - t0, 2),
            'total': total,
            'new': new
        }
        airtab_log.insert(this_dict, typecast=True)

    return wrap_it_up
