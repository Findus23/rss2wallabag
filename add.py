import sys
import yaml
from urllib.parse import urlparse

with open("sites.yaml", 'r') as stream:
    sites = yaml.safe_load(stream)

try:
    name = sys.argv[1]
    feedurl = input("URL: ")
    parsed = urlparse(feedurl)
    if not (parsed.scheme and parsed.netloc and parsed.path):
        print("invalid URL")
        exit()
    tags = []
    while True:
        tag = input("Tag: ")
        if tag == "":
            break
        tags.append(tag)

    sites[name] = {"url": feedurl, "tags": tags}

except Exception as e:
    print("invalid input")
    print(e)

with open('sites.yaml', 'w') as outfile:
    yaml.dump(sites, outfile, default_flow_style=False)
