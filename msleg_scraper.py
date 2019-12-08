# !/usr/bin/env python3
import os
import time
import requests
from twython import Twython
from PIL import Image
import send2trash
from simplediff import html_diff
import imgkit
from airtable import Airtable

airtab = Airtable(os.environ['msleg_db'], 'log',
                  os.environ['AIRTABLE_API_KEY'])

tw = Twython(os.environ['TWITTER_APP_KEY'],
             os.environ['TWITTER_APP_SECRET'],
             os.environ['TWITTER_OAUTH_TOKEN'],
             os.environ['TWITTER_OAUTH_TOKEN_SECRET'])


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
        <link rel=\"stylesheet\" href=\"../style.css\">
    </head>
    <body>
        <p>
        {diff}
        </p>
    </body>\n</html >"""
    css = f"/{os.getenv('HOME')}/code/msleg_scraper/output/diffs/style.css"
    imgkit.from_string(html_string, diff_fn, css=css)
    with open(diff_fn, 'rb') as diff_pic:
        res = tw.upload_media(media=diff_pic)
    tw.update_status(status='testing diff',
                     media_ids=res['media_id'],
                     in_reply_to_status_id=new_tweet_id)


def scrape_cmte_schedules(data):
    t0 = time.time()
    outcomes = []
    records = airtab.search('status', 'current')
    for record in records:
        this_dict = {}
        r = requests.get(record['fields']['url'])
        lines = r.text.splitlines()
        this_dict['last printed'] = lines[3].strip().replace(
            'Printed as of ', '')
        if this_dict['last printed'] != record['fields']['last printed']:
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
            with open(tw_fn, 'rb') as photo:
                response = tw.upload_media(media=photo)
            tweet = tw.update_status(status=msg, media_ids=[
                response['media_id']])
            this_dict['twitter'] = str(tweet['id'])
            new_r = airtab.insert(this_dict)
            send2trash.send2trash(tw_fn)
            get_diff(new_r['id'], this_dict['twitter'])
        else:
            outcomes.append(
                f"the {record['fields']['variable']} is still the version from {record['fields']['last printed']}")
    outcomes.append(
        f'msleg cmte scraper is 👌. It took {round(time.time() - t0, 2)} seconds.')
    data['Value2'] = '\n'.join(outcomes)


def main():
    data = {'Value1': 'msleg_scraper.py'}
    scrape_cmte_schedules(data)
    data['Value3'] = 'success'
    ifttt_event_url = os.environ['IFTTT_WEBHOOKS_URL'].format('msleg_scraper')
    requests.post(ifttt_event_url, json=data)


if __name__ == "__main__":
    main()
