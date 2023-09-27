# !/usr/bin/env python
import os
import time
import pyopenstates
from airtable import Airtable

pyopenstates.set_api_key(os.environ['OPENSTATES_API_KEY'])
airtab = Airtable(os.environ['xxxp_db'], 'legislation', os.environ['AIRTABLE_API_KEY'])


def update_bills(quiet=True):
    records = airtab.get_all(view='2023')
    for record in records:
        os_data = pyopenstates.get_bill(state='ms', session='2023', bill_id=record['fields']['bill_id'])
        last_action = os_data['actions'][len(os_data['actions'])-1]
        this_dict = {}
        this_dict['py_actions_count'] = len(os_data['actions'])
        this_dict['py_last_action'] = last_action['action']
        this_dict['py_last_action_date'] = last_action['date'][:10]
        airtab.update(record['id'], this_dict)
        if not quiet:
            print(record['fields']['py_bill_id'], ': ', this_dict)
        time.sleep(1)


def main():
    update_3xp_bills_v2()


if __name__ == "__main__":
    main()
