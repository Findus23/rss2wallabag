from pprint import pprint

import requests


def get_starred_repos(username):
    r = requests.get("https://api.github.com/users/{user}/starred".format(user=username))
    stars = r.json()
    feeds = []
    for repo in stars:
        feeds[repo["full_name"]] = {"url": repo["url"] + "/releases.atom", "tags": ["github", repo["name"]]}
    return feeds
