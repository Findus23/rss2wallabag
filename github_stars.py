import requests


def get_starred_repos(username, feeds):
    r = requests.get("https://api.github.com/users/{user}/starred".format(user=username))
    stars = r.json()
    for repo in stars:
        if repo["full_name"] not in feeds:
            feeds[repo["full_name"]] = {
                "url": repo["html_url"] + "/releases.atom",
                "tags": ["github", repo["name"]],
                "github": True
            }
    return feeds
