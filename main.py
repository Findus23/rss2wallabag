import copy
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
        yaml = copy.deepcopy(sites)
    except (yaml.YAMLError, FileNotFoundError) as exception:
        print(exception)
        sites = None
        exit(1)

token = Wallabag.get_token(**config["wallabag"])

wall = Wallabag(host=config["wallabag"]["host"], client_secret=config["wallabag"]["client_secret"],
                client_id=config["wallabag"]["client_id"], token=token)

sites.update(github_stars.get_starred_repos(config["github_username"]))

for sitetitle, site in sites.items():
    f = feedparser.parse(site["url"])
    # feedtitle = f["feed"]["title"]
    print(sitetitle)
    if site["latest_article"]:
        for article in f.entries:
            if article.title == site["latest_article"]:
                print("already added: " + article.title)
                break
            print(article.title)
            taglist = [sitetitle]
            if site["tags"]:
                taglist.extend(site["tags"])
            tags = ",".join(taglist)
            if "published_parsed" in article:
                published = mktime(article.published_parsed)
            elif "updated_parsed" in article:
                published = mktime(article.updated_parsed)
            else:
                published = None
            wall.post_entries(url=article.link, title=article.title, tags=tags)
    yaml[sitetitle]["latest_article"] = f.entries[0].title

with open("db.yaml", 'w') as stream:
    yaml.dump(yaml, stream, default_flow_style=False)
