import requests
import yaml
from wallabag_api.wallabag import Wallabag

with open("config.yaml", 'r') as stream:
    try:
        config = yaml.load(stream)
    except (yaml.YAMLError, FileNotFoundError) as exception:
        print(exception)
        config = None
        exit(1)

token = Wallabag.get_token(**config["wallabag"])

wall = Wallabag(host=config["wallabag"]["host"], client_secret=config["wallabag"]["client_secret"],
                client_id=config["wallabag"]["client_id"], token=token)

a=wall.get_entries(tags=["Golem"])
print(a)
b=a["_embedded"]
c=b["items"]
print(c)
exit()

try:
    for i in c[1:]:
        print(i["id"])
        wall.delete_entries(i["id"])
        print(i["id"])
except requests.exceptions.HTTPError as a:
    print(a)
    pass
