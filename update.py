#!/usr/bin/env python3

from scrape import parse_alt
import json
import os
import fire, tqdm

def update_alt(elt):
    """Return the meme entry with the alt-text updated"""
    if type(elt["alt"]) != str:
        # Don't try to update if it isn't a string
        return elt
    elt["alt"] = parse_alt(elt["alt"], "title" in elt)
    return elt

def update_file(fname):
    """Read a file """
    with open(fname) as inp:
        data = json.load(inp)
    data = [update_alt(d) for d in data]
    with open(fname, 'w') as out:
        json.dump(data, out, indent=2)

def update_directory(directory, fname="scrape.json"):
    """Update a directory of meme scrapes"""
    for d in tqdm.tqdm(os.listdir(directory)):
        f = os.path.join(directory, d, fname)
        if os.path.exists(f):
            update_file(f)

if __name__ == "__main__":
    fire.Fire(update_directory)
