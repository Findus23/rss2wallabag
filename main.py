import feedparser
import yaml
from pocket import Pocket

with open("config.yaml", 'r') as stream:
    try:
        config = yaml.load(stream)
    except yaml.YAMLError as exception:
        print(exception)
        config = {"urls": "test"}
        exit(1)

try:
    with open("db.yaml", 'r') as stream:
        db = yaml.load(stream)
except yaml.YAMLError as exception:
    print(exception)
    exit(1)
    db = {}
except FileNotFoundError as exception:
    db = {"titles": {}}

p = Pocket(
    consumer_key=config["consumer_key"],
    access_token=config["access_token"]
)
for url in config["urls"]:
    f = feedparser.parse(url)
    feedtitle = f["feed"]["title"]
    print(feedtitle)
    if feedtitle not in db["titles"]:
        db["titles"][feedtitle] = []
    for article in f.entries:
        if article.title not in db["titles"][feedtitle]:
            print(article.title)
            # r = requests.get(
            #     'https://www.instapaper.com/api/add',
            #     auth=(config["user"], config["password"]),
            #     data={"url": article.link, "title": article.title}
            # )
            # if r.status_code != 201:
            #     print("Return code: " + str(r.status_code))
            #     exit(1)
            p.bulk_add(url=article.link, item_id=None, title=article.title)
            db["titles"][feedtitle].append(article.title)

p.commit()

with open("db.yaml", 'w') as stream:
    yaml.dump(db, stream, default_flow_style=False)
