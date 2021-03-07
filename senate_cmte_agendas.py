#!/usr/bin/env python
import io
import os
import time
import requests
import send2trash

from airtable import Airtable
from pdf2image import convert_from_bytes
from PyPDF2 import PdfFileReader
from twython import Twython

airtab = Airtable(os.environ['msleg_db'], 'cmte_agendas', os.environ['AIRTABLE_API_KEY'])
tw = Twython(os.environ['TWITTER_APP_KEY'], os.environ['TWITTER_APP_SECRET'],
             os.environ['TWITTER_OAUTH_TOKEN'], os.environ['TWITTER_OAUTH_TOKEN_SECRET'])
url = 'http://legislature.ms.gov/media/1151/2021_senate_committee_agendas.pdf'


def extract_information():
    response = requests.get(url)
    this_dict = {}
    with io.BytesIO(response.content) as f:
        this_pdf = PdfFileReader(f)
        this_dict['number_of_pages'] = this_pdf.getNumPages()
        information = dict(this_pdf.getDocumentInfo())
        this_dict['p1_txt'] = this_pdf.getPage(0).extractText()
    this_dict['author'] = information.get('/Author')
    this_dict['creator'] = information.get('/Creator')
    this_dict['modification_datetime'] = information.get('/ModDate').replace('D:', '').replace("'", "")
    this_dict['creation_datetime'] = information.get('/CreationDate').replace('D:', '').replace("'", "")
    this_dict['producer'] = information.get('/Producer')

    s = this_dict['p1_txt'].find('Agendas') + 7
    e = this_dict['p1_txt'].find('Please') - 6
    this_dict['raw_datetime'] = this_dict['p1_txt'][s:e].strip().replace('\n', '')
    this_dict['pdf'] = [{"url": url}]

    matching_record = airtab.match('modification_datetime', this_dict['modification_datetime'])
    if matching_record:
        return
    new_record = airtab.insert(this_dict, typecast=True)
    return new_record['id']


def get_images():
    the_media_ids = []
    os.chdir(f"/{os.getenv('HOME')}/code/msleg_scraper/output/agendas")
    response = requests.get(url)
    pages = convert_from_bytes(response.content)
    for idx, page in enumerate(pages):
        this_fn = f'page_{idx + 1}.jpg'
        page.save(this_fn, 'JPEG')
        time.sleep(2)
        photo = open(this_fn, 'rb')
        response = tw.upload_media(media=photo)
        the_media_ids.append(response['media_id'])
    return the_media_ids


def tweet_with_images(rid, mids):
    record = airtab.get(rid)
    tw.update_status(status=record['fields']['msg'], media_ids=mids)
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
