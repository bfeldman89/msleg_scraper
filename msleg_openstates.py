# !/usr/bin/env python3
import os
import time
from datetime import date, timedelta
from airtable import Airtable
import pyopenstates

OPENSTATES_API_KEY = 'd1767663-d765-474d-b3ad-98a59eab9b3c'
pyopenstates.set_api_key(OPENSTATES_API_KEY)


def update_3xp_bills():
    airtable = Airtable('appw0DSPkfcrhmzmi', 'legislation', os.environ['AIRTABLE_API_KEY'])
    yesterday = date.today() - timedelta(1)
    yesterday_iso = yesterday.isoformat()
    bills = pyopenstates.search_bills(state='ms', updated_since=yesterday_iso)
    print(str(len(bills)) + ' bills updated since yesterday')
    i = 0
    for x in bills:
        record = airtable.match('py_bill_id', x['bill_id'], view='py_2020')
        if record:
            i += 1
            last_action = x['actions'][len(x['actions'])-1]
            this_dict = {}
            this_dict['py_actions_count'] = len(x['actions'])
            this_dict['py_last_action'] = last_action['action']
            this_dict['py_last_action_date'] = last_action['date'][:10]
            airtable.update(record['id'], this_dict)
        else:
            pass
    print(str(i) + ' bills were of interest')


def main():
    update_3xp_bills()


if __name__ == "__main__":
    main()
