import functools

import requests
import toolz
from hash_cache.hash_cache import (
    HashCached,
    calc_kwargs_stem,
)


base_api_url = "https://hacker-news.firebaseio.com/v0"
json_hash_cache = HashCached.json_hash_cache(
    path="~/.local/share/hn_fetcher/cache", calc_stem=calc_kwargs_stem
)


def get_json(url):
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()


def get_hackernews_item(*, item_id):
    return get_json(f"{base_api_url}/item/{item_id}.json")


@functools.cache
def get_hackernews_maxitem():
    return get_json(f"{base_api_url}/maxitem.json")


@toolz.curry
def gen_hackernews_stories(maxitem, n, cacher=json_hash_cache):
    f = cacher(f=get_hackernews_item) if cacher else get_hackernews_item
    g = toolz.excepts(
        requests.exceptions.SSLError,
        f,
    )
    gen = (g(item_id=item_id) for item_id in range(maxitem - n, maxitem))
    gen = filter(None, gen)
    yield from gen
