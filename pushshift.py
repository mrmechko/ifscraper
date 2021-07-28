#!/usr/bin/env python3

import requests
import fire
import json
import sys
import datetime
import tqdm
import time

class RedditMemeQuery(object):
    """Basic class to hold a reddit query. Can be saved or loaded as jso
    - pushshift.io has far too many parameters and I simply don't care about all of them
    - I can handle sorting, I really care about times and content
    """
    def __init__(self,
                 q:str=None,
                 sort:str=None,
                 subreddit:str=None,
                 before:int=None, after:int=None,
                 pinned:bool=None,
                 stickied:bool=None,
                 category:str=None,
                 is_video:bool=None,
                 title:str=None,
                 selftext:str=None,
                 api_url:str="https://api.pushshift.io/reddit/submission/search"):
        self.args = {x: y for x, y in locals().items() if x not in ["self", "api_url"] and y != None}
        self.api_url = api_url

    def params(self):
        return {x: y for x, y in self.args.items()}

    def query(self, raw: bool=False):
        response = requests.get(self.api_url, params=self.params())
        #print(response.url, file=sys.stderr)
        #print(self.params())
        #print(response.text)
        if raw:
            return response.json()
        return json.dumps(response.json(), indent=2)

    def span(self, start_days: int, num_days: int, raw: bool=False):
        """Return a scrape for each day period between start_days and end_days.#!/usr/bin/env python
        start_days and end_days are relative values. start_days should be less than end_days
        """
        dt = datetime.datetime.now()
        today = datetime.datetime(year=dt.year, month=dt.month, day=dt.day)
        delta = datetime.timedelta(days=1)
        start_date = today - datetime.timedelta(days=start_days)

        results = {}

        for i in tqdm.tqdm(range(num_days)):
            time.sleep(1)
            index = start_date.strftime("%Y-%m-%d")
            self.args["after"] = int(start_date.timestamp())
            start_date = start_date + delta
            self.args["before"] = int(start_date.timestamp())
            results[index] = self.query(raw=True)
        if raw:
            return results
        return json.dumps(results, indent=2)


if __name__ == "__main__":
    fire.Fire(RedditMemeQuery)
