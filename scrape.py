#!/usr/bin/env python

from requests_html import HTMLSession
import urllib.request
import json, sys, os, traceback, re, time

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--output", help="output directory for files")
parser.add_argument("--url", help="image flip url")
parser.add_argument("--num", help="number of memes to scrape (default=10)", default=10, type=int)
args = parser.parse_args()

template = """<div class="base-unit clearfix"><h2 class="base-unit-title"><a href={href}>{title}</a></h2><div class="base-img-wrap-wrap"><div class="base-img-wrap" style="{img_width_wrap}"><a class="base-img-link" href="{base_link}" style="padding-bottom:112.5%"><img class="base-img" src="{img}" alt="{alt}"></a></div></div><div class="base-info"><div class="base-author">by <a class="u-username" href="{usr_name_url}">{usr}</a></div><div class="base-view-count">{info}</div>"""
# href
# title
# img_width_wrap
# img
# alt
# view_count
# usr
# upvotes

def get_name(url, output):
    trimmed = re.sub(r'https?:\/\/', '', url)
    trimmed = trimmed.replace("/", "_")
    return os.path.join(output, trimmed)

def get_img(url, output, replace=False):
    #if the url is not an image, continue
    if url.split(".")[-1] not in ["jpg", "png", "gif"]:
        print("not an image:", url, file=sys.stderr)
        return

    #if the image already exists, return unless replace
    if replace or not os.path.isfile(output):
        try:
            urllib.request.urlretrieve(url, output, )
            print("retrieved", url, file=sys.stderr)
        except:
            print("failed to get", url, file=sys.stderr)
            traceback.print_exc()


def scrape(url, output, num, replace=False):
    img_dir = os.path.join(output, "img")
    if not os.path.isdir(output):
        os.mkdir(output)
    if not os.path.isdir(img_dir):
        os.mkdir(img_dir)

    session = HTMLSession()
    page = session.get(url)
    res = []

    while len(res) < num:
        page.html.render()
        for r in page.html.search_all(template):
            image_url = "https:"+r["img"]
            image_name = get_name(image_url, output)
            get_img(image_url, image_name, replace=replace)
            meta = dict(img=image_name, url=image_url, alt=r["alt"], info=r["info"], user=r["usr"])
            res.append(meta)
            print(json.dumps(meta, indent=2))
            time.sleep(2)
        next_url = page.html.next()
        page = session.get(next_url)

    with open(os.path.join(output, "scrape.json"), "w") as f:
        json.dump(res, f)

if __name__ == '__main__':
    url = args.url
    output = args.output
    num = int(args.num)

    # set headers for urllib
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)


    scrape(url, output, num)
