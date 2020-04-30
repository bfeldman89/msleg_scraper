# !/usr/bin/env python
import os
import time
from datetime import date, timedelta
import pyopenstates
from airtable import Airtable

OPENSTATES_API_KEY = 'd1767663-d765-474d-b3ad-98a59eab9b3c'
pyopenstates.set_api_key(OPENSTATES_API_KEY)
airtab = Airtable('appw0DSPkfcrhmzmi', 'legislation', os.environ['AIRTABLE_API_KEY'])


def update_3xp_bills():
    yesterday = date.today() - timedelta(1)
    yesterday_iso = yesterday.isoformat()
    bills = pyopenstates.search_bills(state='ms', search_window='session', updated_since=yesterday_iso)
    print(str(len(bills)) + ' bills updated since yesterday')
    i = 0
    for x in bills:
        record = airtab.match('py_bill_id', x['bill_id'], view='py_2020')
        if record:
            i += 1
            last_action = x['actions'][len(x['actions'])-1]
            this_dict = {}
            this_dict['py_actions_count'] = len(x['actions'])
            this_dict['py_last_action'] = last_action['action']
            this_dict['py_last_action_date'] = last_action['date'][:10]
            airtab.update(record['id'], this_dict)
        else:
            pass
    print(str(i) + ' bills were of interest')


def update_3xp_bills_v2():
    records = airtab.get_all(view='py_2020')
    for record in records:
        os_data = pyopenstates.get_bill(state='ms', term='2020', bill_id=record['fields']['py_bill_id'])
        last_action = os_data['actions'][len(os_data['actions'])-1]
        this_dict = {}
        this_dict['py_actions_count'] = len(os_data['actions'])
        this_dict['py_last_action'] = last_action['action']
        this_dict['py_last_action_date'] = last_action['date'][:10]
        airtab.update(record['id'], this_dict)
        time.sleep(1)


def main():
    # update_3xp_bills()
    # initial code is inefficient but may be necessary for initial
    # few weeks of a legislative session for reasons that aren't clear
    update_3xp_bills_v2()


if __name__ == "__main__":
    main()
