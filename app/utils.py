import requests

h = {
    "Authorization": "Bearer 7112d23e618e967f9475ce6d28a391e50d7ff6924bec1c400ae9a13122d6eede"
}

def check_maker(username):
    url = "https://api.getmakerlog.com/users/{}/"
    r = requests.get(url.format(username))
    if r.status_code == requests.codes.ok:
        return True
    return False

def votes(id,uid):
    l = []
    page = 1
    count = 0
    while True:
        url = "https://api.producthunt.com/v1/posts/{}/votes?page={}"
        r = requests.get(url.format(id,page), headers=h)
        response = r.json()
        page += 1
        if not response.get("votes"):
            break
        for i in response.get("votes"):
            username = i.get("user").get("username")
            image = i.get("user").get("image_url").get("30px")
            name = i.get("user").get("name")
            is_maker = check_maker(username)
            if is_maker:
                l.append(dict(username=username, image=image, name=name, is_maker=is_maker))
            count += 1
    return count, l

def search(url_search, uid):
    import re
    content = requests.get(url_search).text
    resp = re.search('producthunt\:\/\/post\/(?P<id>[0-9]+)', content)
    if resp:
        id =  resp.groupdict().get("id")
        if id:
            return votes(id, uid)
