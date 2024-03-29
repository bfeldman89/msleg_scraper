#!/usr/bin/env python
import os
import time
import requests
from PIL import Image
import send2trash
from simplediff import html_diff
import imgkit

from common import airtab_msleg as airtab, client_v1, client_v2, wrap_from_module


wrap_it_up = wrap_from_module('msleg_scraper.py')


def get_diff(new_record_id, new_tweet_id):
    this_record = airtab.get(new_record_id)
    os.chdir(f"/{os.getenv('HOME')}/code/msleg_scraper/output/diffs")
    new_str = this_record['fields']['string'].replace('\n', ' $ ')
    old_str = this_record['fields']['old string'].replace('\n', ' $ ')
    diff = html_diff(old_str, new_str).replace('$', '<br />')
    diff_fn = f"{this_record['id']}.jpg"
    html_string = f"""<html lang=\"en\">
    <head>
        <meta charset=\"utf-8\">
        <link rel=\"stylesheet\" href=\"https://bfeldman89.com/projects/botfeldman89/src/style.css\">
    </head>
    <body>
        <p>
        {diff}
        </p>
    </body>\n</html >"""
    imgkit.from_string(html_string, diff_fn)
    time.sleep(3)
    media = client_v1.media_upload(filename=diff_fn)
    media_id = media.media_id
    client_v2.create_tweet(text='cmte. schedule diff', media_ids=[media_id], in_reply_to_tweet_id=new_tweet_id)


def scrape_cmte_schedules():
    t0, i = time.time(), 0
    outcomes = []
    records = airtab.search('status', 'current')
    for record in records:
        this_dict = {}
        r = requests.get(record['fields']['url'], timeout=30)
        lines = r.text.splitlines()
        this_dict['last printed'] = lines[3].strip().replace(
            'Printed as of ', '')
        if this_dict['last printed'] != record['fields']['last printed']:
            i += 1
            # SAVE IT AS IMAGE
            tw_fn = record['fields']['variable'].lower().replace(
                ' ', '_') + '.jpg'
            imgkit.from_url(record['fields']['url'], tw_fn)
            time.sleep(2)
            img = Image.open(tw_fn)
            cropped_img = img.crop((0, 0, 640, img.size[1]))
            cropped_img.save(tw_fn)
            time.sleep(2)
            # SCRAPE ALL THE DATA
            this_dict['old string'] = record['fields']['string']
            this_dict['url'] = record['fields']['url']
            this_dict['twitter'] = 'ready'
            this_dict['status'] = 'current'
            this_dict['variable'] = record['fields']['variable']
            this_dict['script'] = record['fields']['script']
            this_dict['string'] = r.text.replace("<HTML><PRE>", "").replace("</pre></html>", "").replace(
                "________________________________________________________________________________\r\nLEGEND: WNM = Will Not Meet, TBA = To Be Announced, \r\n    BC = Before Convening, AA = After Adjournment,\r\n    AR = After Recess", "")
            this_dict['diff'] = html_diff(
                record['fields']['string'], this_dict['string'])
            # NOW WE CAN UPDATE THE NO LONGER CURRENT RECORD TO `OLD`
            airtab.update(record['id'], fields={'status': 'old'})
            # NOW LETS TWEET IT
            msg = f"The #msleg {this_dict['variable']} was updated on {this_dict['last printed']}"
            outcomes.append(msg)
            media = client_v1.media_upload(filename=tw_fn)
            media_id = media.media_id
            tweet = client_v2.create_tweet(text=msg, media_ids=[media_id])
            this_dict['twitter'] = tweet[0]['id']
            new_r = airtab.insert(this_dict)
            send2trash.send2trash(tw_fn)
            # NOW LETS REPLY TWEET THE DIFF
            get_diff(new_r['id'], this_dict['twitter'])
    wrap_it_up(t0, new=i, total=2, function='scrape_cmte_schedules')


def main():
    scrape_cmte_schedules()


if __name__ == "__main__":
    main()
