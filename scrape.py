#!/usr/bin/env python

import json, sys, os, traceback, re, time, tqdm
import urllib.request
import argparse
from requests_html import HTMLSession

parser = argparse.ArgumentParser()
parser.add_argument("--output", help="output directory for files")
parser.add_argument("--url", help="image flip url")
parser.add_argument("--num", help="number of memes to scrape (default=10)", default=10, type=int)
args = parser.parse_args()

# set headers for urllib
opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
urllib.request.install_opener(opener)

# Our template has the following entries
# href : link to the post
# title : title of the post
# img_width_wrap
# base_link : link to the post
# img : link to the image
# alt : alt text - usually including ocr'd text
# user_name_url : url to the user profile
# usr : username
# info : meta info about the post, including upvote, view, and comment counts
TEMPLATE = """<div class="base-unit clearfix">
<h2 class="base-unit-title">
<a href={href}>{title}</a>
</h2>
<div class="base-img-wrap-wrap">
<div class="base-img-wrap" style="{img_width_wrap}">
<a class="base-img-link" href="{base_link}" style="padding-bottom:112.5%">
<img class="base-img" src="{img}" alt="{alt}">
</a>
</div>
</div>
<div class="base-info">
<div class="base-author">by <a class="u-username" href="{usr_name_url}">{usr}</a></div>
<div class="base-view-count">{info}</div>"""
TEMPLATE2 = TEMPLATE.replace("\"", "'")

def get_name(url, output):
    """Convert the url for an image to a filename"""
    trimmed = re.sub(r'https?:\/\/', '', url)
    trimmed = trimmed.replace("/", "_")
    return os.path.join(output, "img", trimmed)

def get_img(url, output, replace=False):
    """Get an image from a url and save in output. if replace is false, skip files that already exist"""
    #if the url is not an image, continue
    if url.split(".")[-1] not in ["jpg", "png", "gif"]:
        print("not an image:", url, file=sys.stderr)
        return

    #if the image already exists, return unless replace
    if replace or not os.path.isfile(output):
        try:
            urllib.request.urlretrieve(url, output, )
            # print("retrieved", url, file=sys.stderr)
        except:
            print("failed to get", url, file=sys.stderr)
            traceback.print_exc()

def parse_info(info):
    """Parse the info string into something more useful"""
    info = info.replace(",", "").split()
    res = dict(comments=0, upvotes=0, views=0)
    if "upvotes" in info:
        res["upvotes"] = int(info[info.index("upvotes") - 1])
    if "views" in info:
        res["views"] = int(info[info.index("views") - 1])
    if "comments" in info:
        res["comments"] = int(info[info.index("comments") - 1])
    return res

def scrape(url, output, num, replace=False):
    """Scrape all posts from a specific imgflip page."""
    img_dir = os.path.join(output, "img")
    if not os.path.isdir(output):
        os.mkdir(output)
    if not os.path.isdir(img_dir):
        os.mkdir(img_dir)

    session = HTMLSession()
    page = session.get(url.split("/")[-1])
    res = []

    pbar = tqdm.tqdm(total=num)
    pbar.set_description(url)
    while len(res) < num:
        page.html.render()
        # print(page.html)
        for r in page.html.find("div.base-unit"):
            # print(r)
            try:
                img_link = r.find("img.base-img", first=True)
                img = img_link.attrs["src"]
                image_url = "https:"+img
                image_name = get_name(image_url, output)
                get_img(image_url, image_name, replace=replace)
                meta = dict(img=image_name, url=image_url, alt=img_link.attrs["alt"], info=parse_info(r.find("div.base-view-count", first=True).text), user=r.find("a.u-username", first=True).text, title=r.find("h2 > a", first=True).text)
                res.append(meta)
                pbar.update(1)
                # print(json.dumps(meta, indent=2))
            except:
                print("failed to retrieve meme")
            time.sleep(2)
        next_url = page.html.next()
        pbar.set_description(next_url.split("/")[-1])
        page = session.get(next_url)

    with open(os.path.join(output, "scrape.json"), "w") as f:
        json.dump(res, f, indent=2)

def load_batch(f, num=100, batch_name="batch"):
    with open(f) as inp:
        data = json.load(inp)
        for d in data:
            gen = d["generator"].split("/")[-1]
            d["code"] = gen
            url = f"https://imgflip.com/meme/{gen}"
            # print(f"scraping {url}")
            output = f"{batch_name}/{gen}"
            scrape(url, output, num)
    with open(f, "w") as outf:
        json.dump(data, outf, indent=2)

if __name__ == '__main__':
    url = args.url
    output = args.output
    num = int(args.num)


    scrape(url, output, num)
