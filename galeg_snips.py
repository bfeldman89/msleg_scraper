# !/usr/bin/env python
import os
import time
from datetime import date, timedelta
from airtable import Airtable
import pyopenstates

pyopenstates.set_api_key(os.environ['OPENSTATES_API_KEY'])

def get_ga_bills():
    airtable = Airtable('appGm06z3pp0knK0K', 'bills', os.environ['AIRTABLE_API_KEY'])
    records = airtable.get_all(view='to-scrape', fields=['bill_no'])
    def get_ga_bill_deets():
        for record in records:
            try:
                x = pyopenstates.get_bill(state='ga', session='2023_24', bill_id=record['fields']['bill_no'], include=['sponsorships', 'abstracts'])
                time.sleep(2)
            except pyopenstates.NotFound as err:
                print(err)
                continue
            this_dict = {}
            py_sponsors=[]
            py_cosponsors = []
            this_dict['first_action_date'] = x['first_action_date']
            this_dict['latest_action_date'] = x['latest_action_date']
            this_dict['latest_action_description'] = x['latest_action_description']
            this_dict['latest_passage_date'] = x['latest_passage_date']
            this_dict['guid'] = str(x['extras']['guid'])
            this_dict['title'] = x['title']
            if len(x['abstracts']) == 1:
                this_dict['abstract'] =x['abstracts'][0]['abstract']
            for sponsor in x['sponsorships']:
                if sponsor['primary']:
                    py_sponsors.append(sponsor['name'])
                # else:
                    # py_cosponsors.append(sponsor['name'])
            this_dict['py_sponsors'] = ','.join(py_sponsors)
            # this_dict['py_cosponsors'] = ','.join(py_cosponsors)
            airtable.update(record['id'], this_dict, typecast=True)


