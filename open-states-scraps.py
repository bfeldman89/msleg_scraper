OPENSTATES_API_KEY = 'd1767663-d765-474d-b3ad-98a59eab9b3c'
OPENSTATES_API_KEY_2 = 'e32b40a7-d2f6-4078-9137-313906fecc05'
OPENSTATES_API_KEY_3 = '161f083e-f16e-4a17-be0b-4aeb73cae6f8'
OPENSTATES_API_KEY_4 = '08602c6d-bb0b-4839-900e-b26f2dbc010c'


pyopenstates.set_api_key(os.environ['OPENSTATES_API_KEY'])


airtab = Airtable(os.environ['msleg_db'], 'bills', os.environ['AIRTABLE_API_KEY'])
records = airtab.get_all(view='2023', fields=['bill_id'])

def update_bills(quiet=True):
    for record in records:
        os_data = pyopenstates.get_bill(state='ms', session='2023', bill_id=record['fields']['bill_id'], include=['sponsorships'])
        this_dict = {}
        # cosponsors = []
        this_dict['created_at'] = str(os_data['created_at'].isoformat())
        this_dict['updated_at'] = str(os_data['updated_at'].isoformat())
        this_dict['title'] = os_data['title']
        this_dict['scraped_subjects'] = os_data['subject']
        this_dict['last_action'] = os_data['latest_action_description']
        this_dict['first_action_date'] = os_data['first_action_date']
        this_dict['last_action_date'] = os_data['latest_action_date']
        this_dict['summary'] = os_data['extras']['summary']
        list_of_sponsor_data = os_data['sponsorships']
        for sponsor_data in list_of_sponsor_data:
            if sponsor_data['primary']:
                try:
                    this_dict['primary_sponsor'] = sponsor_data['person']['name']
                except:
                    this_dict['primary_sponsor'] = sponsor_data['name']
        airtab.update(record['id'], this_dict)
        time.sleep(6.1)

x = {
    'sponsorships': 
        [
            {
                'name': 'Lamar', 
                'entity_type': 'person', 
                'person': {
                    'id': 'ocd-person/c655558e-dfac-468a-a633-85f380c538b6', 
                    'name': 'John Thomas "Trey" Lamar, III', 
                    'party': 'Republican', 
                    'current_role': {'title': 'Representative', 'org_classification': 'lower', 'district': '8', 'division_id': 'ocd-division/country:us/state:ms/sldl:8'}}, 
                'primary': True, 
                'classification': 'primary'}]}

os_data = pyopenstates.get_bill(state='ms', session='2023', bill_id='HB 1027', include=['sponsorships', 'documents'])

'''
OPEN STATES ACCOUNTS

bfeldman892
bfeldman89@pm.me 
twitter botfeldman89
161f083e-f16e-4a17-be0b-4aeb73cae6f8


blakefeldman89@gmail.com
bfeldman@mscenterforjustice.org
github
e32b40a7-d2f6-4078-9137-313906fecc05


blake_feldman@icloud.com
d1767663-d765-474d-b3ad-98a59eab9b3c


botfeldman89
botfeldman89@gmail.com
08602c6d-bb0b-4839-900e-b26f2dbc010c
'''