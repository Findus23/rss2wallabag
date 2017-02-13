from time import mktime

import feedparser
import yaml
from wallabag_api.wallabag import Wallabag
import github_stars

with open("config.yaml", 'r') as stream:
    try:
        config = yaml.load(stream)
    except (yaml.YAMLError, FileNotFoundError) as exception:
        print(exception)
        config = None
        exit(1)
with open("sites.yaml", 'r') as stream:
    try:
        sites = yaml.load(stream)
    except (yaml.YAMLError, FileNotFoundError) as exception:
        print(exception)
        sites = None
        exit(1)
try:
    with open("db.yaml", 'r') as stream:
        db = yaml.load(stream)
except yaml.YAMLError as exception:
    print(exception)
    exit(1)
    db = {}
except FileNotFoundError as exception:
    db = {"sites": {}}

token = Wallabag.get_token(**config["wallabag"])

wall = Wallabag(host=config["wallabag"]["host"], client_secret=config["wallabag"]["client_secret"],
                client_id=config["wallabag"]["client_id"], token=token)

sites.update(github_stars.get_starred_repos(config["github_username"]))

for sitetitle, site in sites.items():
    f = feedparser.parse(site["url"])
    # feedtitle = f["feed"]["title"]
    print(sitetitle)
    if sitetitle not in db["sites"]:
        db["sites"][sitetitle] = []
    for article in f.entries:
        if article.title not in db["sites"][sitetitle]:
            print(article.title)
            tagarray = [sitetitle]
            if site["tags"]:
                tagarray.extend(site["tags"])
            tags = ",".join(tagarray)
            if "published_parsed" in article:
                published = mktime(article.published_parsed)
            elif "updated_parsed" in article:
                published = mktime(article.updated_parsed)
            else:
                published = None
            wall.post_entries(url=article.link, title=article.title, tags=tags)
            db["sites"][sitetitle].append(article.title)

with open("db.yaml", 'w') as stream:
    yaml.dump(db, stream, default_flow_style=False)
