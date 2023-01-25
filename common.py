#!/usr/bin/env python
"""This module provides a function for shipping logs to Airtable."""
import os
import time
from airtable import Airtable
from twython import Twython

airtab_msleg = Airtable(os.environ['msleg_db'], 'log', os.environ['AIRTABLE_API_KEY'])

airtab_agendas = Airtable(os.environ['msleg_db'], 'cmte_agendas', os.environ['AIRTABLE_API_KEY'])

airtab_log = Airtable(os.environ['log_db'],
                      table_name='log',
                      api_key=os.environ['AIRTABLE_API_KEY'])

tw = Twython(os.environ['TWITTER_APP_KEY'], os.environ['TWITTER_APP_SECRET'],
             os.environ['TWITTER_OAUTH_TOKEN'], os.environ['TWITTER_OAUTH_TOKEN_SECRET'])


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
