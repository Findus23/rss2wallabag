import logging
import sys
from dataclasses import dataclass
from datetime import datetime
from time import mktime
from typing import List, Optional, Dict
from urllib.parse import urljoin

import feedparser
import requests
import yaml
from feedparser import FeedParserDict

from api import WallabagAPI


@dataclass
class WallabagConfig:
    host: str
    client_id: str
    client_secret: str
    username: str
    password: str


class Config:
    def __init__(self):
        with open("config.yaml", 'r') as stream:
            data = yaml.safe_load(stream)
        self.wallabag = WallabagConfig(**data["wallabag"])
        if data["github_username"]:
            self.github_username = data["github_username"]
        else:
            self.github_username = None
        self.debug = data["debug"]

    @property
    def production(self):
        return not self.debug


@dataclass
class Site:
    title: str
    url: str
    github: bool
    tags: List[str]
    latest_article: Optional[str]


def load_sites() -> Dict[str, Site]:
    with open("sites.yaml", 'r') as stream:
        data = yaml.safe_load(stream)
    sites: Dict[str, Site] = {}
    for title, entry in data.items():
        if "latest_article" not in entry:
            entry["latest_article"] = None
        if "github" not in entry:
            entry["github"] = None
        sites[title] = Site(title, **entry)
    return sites


def get_starred_repos(username, sites: Dict[str, Site]):
    r = requests.get("https://api.github.com/users/{user}/starred".format(user=username))
    stars = r.json()
    for repo in stars:
        if repo["full_name"] not in sites:
            sites[repo["full_name"]] = Site(
                url=repo["html_url"] + "/releases.atom",
                tags=["github", repo["name"]],
                github=True,
                title=repo["full_name"],
                latest_article=None
            )
    return sites


def main():
    sites = load_sites()
    config = Config()

    logger = logging.getLogger()
    logger.handlers = []
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(logging.WARNING if config.production else logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    fh = logging.FileHandler('debug.log')
    fh.setFormatter(formatter)
    fh.setLevel(logging.WARNING if config.production else logging.DEBUG)
    logger.addHandler(fh)

    wallabag_config = config.wallabag
    api = WallabagAPI(host=wallabag_config.host)
    api.auth(client_secret=wallabag_config.client_secret, client_id=wallabag_config.client_id,
             username=wallabag_config.username, password=wallabag_config.password)

    if config.github_username:
        sites = get_starred_repos(config.github_username, sites)

    new_sites: Dict[str, Dict] = {}
    for title, site in sites.items():
        new_site = handle_feed(api, site, logger, config)
        new_sites[title] = new_site.__dict__
        del new_sites[title]["title"]
    if config.production:
        with open("sites.yaml", 'w') as stream:
            yaml.dump(new_sites, stream, default_flow_style=False)


def handle_feed(api: WallabagAPI, site: Site, logger: logging.Logger, config: Config) -> Site:
    logger.info("Downloading feed: " + site.title)
    r = api.s.get(site.url)
    if r.status_code != 404:
        r.raise_for_status()
    rss = r.text
    logger.info("Parsing feed: " + site.title)
    f = feedparser.parse(rss)
    logger.debug("finished parsing: " + site.title)

    articles: List[FeedParserDict] = f.entries
    for article in articles:
        if article.title == site.latest_article:
            logger.debug("already added: " + article.title)
            break
        logger.info("article found: " + article.title)
        taglist = [site.title]
        if site.tags:
            taglist.extend(site.tags)
        if "published_parsed" in article:
            published = datetime.fromtimestamp(mktime(article.published_parsed))
        elif "updated_parsed" in article:
            published = datetime.fromtimestamp(mktime(article.updated_parsed))
        else:
            published = None
        logger.info("add to wallabag: " + article.title)
        if site.github:
            title = site.title + ": " + article.title
        else:
            title = article.title
        if not hasattr(article, 'link'):
            logger.info("no link, skipping!")
            continue
        url = urljoin(site.url, article.link)
        if api.check_exist(url):
            logger.info("already found in wallabag: " + article.title)
            continue
        if config.production:
            api.add_entry(url=url, title=title, tags=taglist, published=published)
        else:
            logger.info("warning: running in debug mode - not adding links to wallabag")
    if articles:
        site.latest_article = articles[0].title

    return site


if __name__ == '__main__':
    main()
