import logging
from time import mktime

import feedparser
import sys
import yaml
from raven import Client
from wallabag_api.wallabag import Wallabag

import github_stars
import golem_top

logger = logging.getLogger()
logger.handlers = []
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

ch = logging.StreamHandler(stream=sys.stdout)
ch.setLevel(logging.WARNING)
ch.setFormatter(formatter)
logger.addHandler(ch)

fh = logging.FileHandler('debug.log')
fh.setFormatter(formatter)
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

with open("config.yaml", 'r') as stream:
    try:
        config = yaml.load(stream)
    except (yaml.YAMLError, FileNotFoundError) as exception:
        logger.error(exception)
        config = None
        exit(1)
with open("sites.yaml", 'r') as stream:
    try:
        sites = yaml.load(stream)
    except (yaml.YAMLError, FileNotFoundError) as exception:
        logger.error(exception)
        sites = None
        exit(1)

if "sentry_url" in config:
    client = Client(
        dsn=config["sentry_url"],
        processors=(
            'raven.processors.SanitizePasswordsProcessor',
        )
    )

token = Wallabag.get_token(**config["wallabag"])

wall = Wallabag(host=config["wallabag"]["host"], client_secret=config["wallabag"]["client_secret"],
                client_id=config["wallabag"]["client_id"], token=token)

sites = github_stars.get_starred_repos(config["github_username"], sites)

for sitetitle, site in sites.items():
    logger.info(sitetitle + ": Downloading feed")
    # r = requests.get(site["url"])
    logger.info(sitetitle + ": Parsing feed")
    f = feedparser.parse(site["url"])
    logger.debug(sitetitle + ": finished parsing")
    # feedtitle = f["feed"]["title"]
    if "latest_article" in site:
        for article in f.entries:
            if article.title == site["latest_article"]:
                logger.debug("already added: " + article.title)
                break
            logger.info(article.title + ": article found")
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
            logger.info(article.title + ": add to wallabag")
            if "github" in site and site["github"]:
                title = sitetitle + ": " + article.title
            else:
                title = article.title
                # wall.post_entries(url=article.link, title=title, tags=tags)
    else:
        logger.debug(sitetitle + ": no latest_article")
    if f.entries:
        sites[sitetitle]["latest_article"] = f.entries[0].title

# articles = golem_top.get_top_articles()
# params = {
#    'access_token': wall.token,
#    "urls[]": articles
# }
# response = wall.query("/api/entries/exists.{format}".format(format=wall.format), "get", **params)
# for url, old in response.items():
#    if not old:
#        wall.post_entries(url=url, tags="golem,it", title=None)

# print(response)
with open("sites.yaml", 'w') as stream:
    yaml.dump(sites, stream, default_flow_style=False)
