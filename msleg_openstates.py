# !/usr/bin/env python3
import os
from datetime import date, timedelta
from airtable import Airtable
import pyopenstates

OPENSTATES_API_KEY = 'd1767663-d765-474d-b3ad-98a59eab9b3c'
pyopenstates.set_api_key(OPENSTATES_API_KEY)


def get_bills():
    airtable = Airtable('appxbJoRFBRbGgj4s', 'bills', os.environ['AIRTABLE_API_KEY'])
    yesterday = date.today() - timedelta(1)
    yesterday_iso = yesterday.isoformat()
    bills = pyopenstates.search_bills(state='ms', updated_since=yesterday_iso)
    for bill in bills:
        record = airtable.match('bill_id', bill['bill_id'])
        this_dict = {}
        this_dict['bill_id'] = bill['bill_id']
        this_dict['created_at'] = str(bill['created_at'].isoformat())
        this_dict['updated_at'] = str(bill['updated_at'].isoformat())
        this_dict['title'] = bill['title']
        this_dict['session'] = bill['session']
        this_dict['type'] = bill['type']
        this_dict['chamber'] = bill['chamber']
        this_dict['documents'] = str(bill['documents'])
        this_dict['scraped_subjects'] = bill['scraped_subjects']
        this_dict['actions'] = str(bill['actions'])
        this_dict['actions_count'] = len(bill['actions'])
        last_action = bill['actions'][len(bill['actions'])-1]
        this_dict['last_action'] = last_action['action']
        this_dict['last_action_date'] = last_action['date']
        this_dict['last_action_type'] = last_action['type']
        this_dict['last_action_actor'] = last_action['actor']
        if record:
            airtable.update(record['id'], this_dict)
        if not record:
            airtable.insert(this_dict)

    print(str(len(bills)) + ' bills updated since yesterday')

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
