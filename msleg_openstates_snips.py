# !/usr/bin/env python
import os
import time
from datetime import date, timedelta
from airtable import Airtable
import pyopenstates

pyopenstates.set_api_key(os.environ['OPENSTATES_API_KEY'])


def get_bills():
    airtable = Airtable('appxbJoRFBRbGgj4s', 'bills', os.environ['AIRTABLE_API_KEY'])
    yesterday = date.today() - timedelta(1)
    yesterday_iso = yesterday.isoformat()
    bills = pyopenstates.search_bills(state='ms', updated_since=yesterday_iso)
    for bill in bills:
        # record = airtable.match('bill_id', bill['bill_id'])
        record = airtable.match('bill_id', bill['identifier'], view='2023')
        this_dict = {}
        # this_dict['bill_id'] = bill['bill_id']
        this_dict['bill_id'] = bill['identifier']
        this_dict['created_at'] = str(bill['created_at'].isoformat())
        this_dict['updated_at'] = str(bill['updated_at'].isoformat())
        this_dict['title'] = bill['title']
        this_dict['session'] = bill['session']
        # this_dict['documents'] = str(bill['documents'])
        # this_dict['actions'] = str(bill['actions'])
        # this_dict['actions_count'] = len(bill['actions'])
        # last_action = bill['actions'][len(bill['actions'])-1]
        # this_dict['last_action'] = last_action['action']
        # this_dict['last_action_date'] = last_action['date']
        # this_dict['last_action_type'] = last_action['type']
        # this_dict['last_action_actor'] = last_action['actor']
        this_dict['type'] = bill['classification']
        this_dict['chamber'] = bill['from_organization']['classification']
        this_dict['scraped_subjects'] = bill['subject']
        this_dict['last_action'] = bill['latest_action_description']
        this_dict['last_action_date'] = bill['latest_action_date']
        this_dict['first_action_date'] = bill['first_action_date']
        this_dict['summary'] = bill['extras']['summary']
        if record:
            airtable.update(record['id'], this_dict)
        if not record:
            airtable.insert(this_dict)
        time.sleep(.5)

    print(str(len(bills)) + ' bills updated since yesterday')


'''
example bill data from get_bills:

{'id': 'ocd-bill/3301cb8f-d404-4ea8-83dc-90c9547f76c9', 
'session': '2023', 
'jurisdiction': {'id': 'ocd-jurisdiction/country:us/state:ms/government', 'name': 'Mississippi', 'classification': 'state'}, 
'from_organization': {'id': 'ocd-organization/47c2e037-ffe3-46c3-9399-8feb1f7d4988', 'name': 'House', 'classification': 'lower'}, 
'identifier': 'HR 27', 
'title': 'Faye Graham Dillard; commend upon the occasion of her 90th birthday.', 
'classification': ['resolution'], 
'subject': ['Rules'], 
'extras': {'summary': 'A RESOLUTION COMMENDING AND CONGRATULATING MS. FAYE GRAHAM DILLARD UPON THE OCCASION OF HER 90TH BIRTHDAY.'}, 
'created_at': datetime.datetime(2023, 1, 25, 0, 44, 15, 972151, tzinfo=tzutc()), 
'updated_at': datetime.datetime(2023, 1, 25, 0, 44, 15, 989042, tzinfo=tzutc()), 
'openstates_url': 'https://openstates.org/ms/bills/2023/HR27/', 
'first_action_date': '2023-01-16T06:00:00+00:00', 
'latest_action_date': '2023-01-16T06:00:00+00:00', 
'latest_action_description': 'Referred To Rules', 
'latest_passage_date': ''}
'''

def get_ppl():
    airtable = Airtable('appxbJoRFBRbGgj4s', 'legislators', os.environ['AIRTABLE_API_KEY'])
    this_list = pyopenstates.search_legislators(state='ms', active=False)
    print(len(this_list))
    for legislator in this_list:
        record = airtable.match('leg_id', legislator['leg_id'], view='today')
        this_dict = {}
        this_dict['chamber'] = legislator['chamber']
        this_dict['leg_id'] = legislator['leg_id']
        this_dict['created_at'] = str(legislator['created_at'].isoformat())
        this_dict['updated_at'] = str(legislator['updated_at'].isoformat())
        this_dict['full_name'] = legislator['full_name']
        this_dict['first_name'] = legislator['first_name']
        this_dict['last_name'] = legislator['last_name']
        this_dict['suffix'] = legislator['suffix']
        this_dict['photo_url'] = legislator['photo_url']
        this_dict["pic"] = [{"url": legislator['photo_url']}]
        this_dict['url'] = legislator['url']
        this_dict['email'] = legislator['email']
        this_dict['party'] = legislator['party']
        this_dict['district'] = legislator['district']
        this_dict['active'] = legislator['active']
        this_dict['term'] = legislator['roles'][0]['term']
        for office in legislator['offices']:
            if office['type'] == 'capitol':
                this_dict['office_address'] = office['address']
                this_dict['office_phone'] = office['phone']
            elif office['type'] == 'district':
                this_dict['district_office_address'] = office['address']
                this_dict['district_office_phone'] = office['phone']
            else:
                print(this_dict['full_name'], ': ', office['type'])
        if record:
            airtable.update(record['id'], this_dict, typecast=True)
        if not record:
            airtable.insert(this_dict, typecast=True)


def update_3xp_bills_v1():
    # this is no longer used in `msleg_openstates.py`
    # update_3xp_bills_v2() is more efficient
    airtab = Airtable('appw0DSPkfcrhmzmi', 'legislation', os.environ['AIRTABLE_API_KEY'])
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


def initial_3xp_scrapes():
    airtable = Airtable('appw0DSPkfcrhmzmi', 'legislation', os.environ['AIRTABLE_API_KEY'])
    records = airtable.get_all(view='py_2020 copy', fields=['py_bill_id', 'session', 'date_of_outcome'])
    for record in records:
        try:
            x = pyopenstates.get_bill(state='ms', term=record['fields']['session'], bill_id=record['fields']['py_bill_id'])
            time.sleep(1)
        except pyopenstates.NotFound as err:
            print(err)
            continue
        last_action = x['actions'][len(x['actions'])-1]
        this_dict = {}
        this_dict['short_title'] = x['title']
        this_dict['py_actions_count'] = len(x['actions'])
        this_dict['py_last_action'] = last_action['action']
        this_dict['py_last_action_date'] = last_action['date'][:10]
        this_dict['updated_at'] = x['updated_at'].isoformat()
        airtable.update(record['id'], this_dict, typecast=True)


# def update_3xp_bills_v2():
airtable = Airtable('appw0DSPkfcrhmzmi', 'legislation', os.environ['AIRTABLE_API_KEY'])
records = airtable.get_all(view='py_2020 copy', fields=['py_bill_id', 'session'])
for record in records:
    this_dict = {}
    py_cosponsors = []
    x = pyopenstates.get_bill(state='ms', term=record['fields']['session'], bill_id=record['fields']['py_bill_id'])
    for sponsor in x['sponsors']:
        if sponsor['type'] == 'primary':
            this_dict['primary_sponsor_raw'] = sponsor['name']
        else:
            py_cosponsors.append(sponsor['name'])
    this_dict['py_cosponsors'] = ','.join(py_cosponsors)
    this_dict['updated_at'] = x['updated_at'].isoformat()
    airtable.update(record['id'], this_dict, typecast=True)
    time.sleep(1)
