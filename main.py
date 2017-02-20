import copy
from time import mktime

import feedparser
import yaml
from wallabag_api.wallabag import Wallabag
import github_stars

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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

token = Wallabag.get_token(**config["wallabag"])

wall = Wallabag(host=config["wallabag"]["host"], client_secret=config["wallabag"]["client_secret"],
                client_id=config["wallabag"]["client_id"], token=token)

sites = github_stars.get_starred_repos(config["github_username"], sites)

for sitetitle, site in sites.items():
    logger.info(sitetitle + ": Downloading feed")
    f = feedparser.parse(site["url"])
    (sitetitle + ": feed parsed")
    # feedtitle = f["feed"]["title"]
    if "latest_article" in site:
        for article in f.entries:
            if article.title == site["latest_article"]:
                logger.debug("already added: " + article.title)
                break
            logger.info(article.title + ": aricle found")
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
            logger.debug(article.title + ": add to wallabag")
            wall.post_entries(url=article.link, title=article.title, tags=tags)
    else:
        logger.debug(sitetitle + ": no latest_article")
    if f.entries:
        logger.warning(sitetitle + ": Downloading feed")
        sites[sitetitle]["latest_article"] = f.entries[0].title

with open("sites.yaml", 'w') as stream:
    yaml.dump(sites, stream, default_flow_style=False)
