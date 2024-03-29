#!/usr/bin/env python
import io
import os
import time
import requests
import send2trash

from pdf2image import convert_from_bytes
from PyPDF2 import PdfReader

from common import airtab_agendas as airtab, client_v1, client_v2

url = 'http://legislature.ms.gov/media/1151/2023_SENATE_COMMITTEE_AGENDAS.pdf'


def extract_information():
    response = requests.get(url, timeout=60)
    this_dict = {}
    this_dict['url'] = url
    this_dict['header_mod_time'] = response.headers['Last-Modified']
    matching_record = airtab.match('header_mod_time', this_dict['header_mod_time'])
    if matching_record:
        print('PDF has not been modified since last scrape')
        return
    with io.BytesIO(response.content) as f:
        this_pdf = PdfReader(f)
        this_dict['number_of_pages'] = len(this_pdf.pages)
        information = dict(this_pdf.metadata)
        this_dict['p1_txt'] = this_pdf.pages[0].extract_text()
    this_dict['author'] = information.get('/Author')
    this_dict['creator'] = information.get('/Creator')
    this_dict['modification_datetime'] = information.get('/ModDate').replace('D:', '').replace("'", "")
    this_dict['creation_datetime'] = information.get('/CreationDate').replace('D:', '').replace("'", "")
    this_dict['producer'] = information.get('/Producer')
    s = this_dict['p1_txt'].find('Agendas') + 7
    e = this_dict['p1_txt'].find('Meetings in') - 6
    this_dict['raw_datetime'] = this_dict['p1_txt'][s:e].strip().replace('\n', '')
    this_dict['pdf'] = [{"url": url}]
    new_record = airtab.insert(this_dict, typecast=True)
    return new_record['id']


def get_images():
    the_media_ids = []
    os.chdir(f"/{os.getenv('HOME')}/code/msleg_scraper/output/agendas")
    response = requests.get(url, timeout=60)
    pages = convert_from_bytes(response.content)
    for idx, page in enumerate(pages):
        this_fn = f'page_{idx + 1}.jpg'
        page.save(this_fn, 'JPEG')
        time.sleep(2)
        # photo = open(this_fn, 'rb')
        media = client_v1.media_upload(filename=this_fn)
        media_id = media.media_id
        the_media_ids.append(media_id)
    return the_media_ids


def tweet_with_images(rid, mids):
    record = airtab.get(rid)
    # tw.update_status(status=record['fields']['msg'], media_ids=mids)
    msg = record['fields']['msg']
    tweet = client_v2.create_tweet(text=msg, media_ids=mids)
    os.chdir(f"/{os.getenv('HOME')}/code/msleg_scraper/output/agendas")
    for fn in os.listdir('.'):
        send2trash.send2trash(fn)

def main():
    new_rid = extract_information()
    if new_rid:
        media_ids = get_images()
        tweet_with_images(rid=new_rid, mids=media_ids)
    else:
        print('agendas document hasn\'t changed')

if __name__ == '__main__':
    main()
