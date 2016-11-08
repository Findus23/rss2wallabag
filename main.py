from time import mktime

import feedparser
import yaml
from pocket import Pocket

with open("config.yaml", 'r') as stream:
    try:
        config = yaml.load(stream)
    except (yaml.YAMLError, FileNotFoundError) as exception:
        print(exception)
        config = None
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

p = Pocket(
    consumer_key=config["consumer_key"],
    access_token=config["access_token"]
)
for sitetitle, site in config["sites"].items():
    f = feedparser.parse(site["url"])
    # feedtitle = f["feed"]["title"]
    print(sitetitle)
    if sitetitle not in db["sites"]:
        db["sites"][sitetitle] = []
    for article in f.entries:
        if article.title not in db["sites"][sitetitle]:
            print(article)
            if site["tags"]:
                tags = ",".join(site["tags"])
            else:
                tags = None
            if "published_parsed" in article:
                published = mktime(article.published_parsed)
            elif "updated_parsed" in article:
                published = mktime(article.updated_parsed)
            else:
                published = None
            p.bulk_add(url=article.link, item_id=None, title=article.title, tags=tags, time=published)
            db["sites"][sitetitle].append(article.title)

p.commit()

with open("db.yaml", 'w') as stream:
    yaml.dump(db, stream, default_flow_style=False)
