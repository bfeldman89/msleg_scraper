# !/usr/bin/env python
import os
import time
from datetime import date, timedelta
from airtable import Airtable
from documentcloud import DocumentCloud

dc = DocumentCloud(username=os.environ['MUCKROCK_USERNAME'], password=os.environ['MUCKROCK_PW'])

airtable = Airtable('app67LzgAtSoNhma8', 'suffrage restoration bills', os.environ['AIRTABLE_API_KEY'])

records = airtable.get_all(view='needs dc')
print(len(records))
for record in records:
    pdf_link = record['fields']['msleg_link']
    obj = dc.documents.upload(pdf_link)
    airtable.update(record['id'], fields={'dc_id': str(obj.id)})
    time.sleep(1)