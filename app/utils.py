import requests
from django.core.cache import cache

h = {
    "Authorization": "Bearer 7112d23e618e967f9475ce6d28a391e50d7ff6924bec1c400ae9a13122d6eede"
}

def check_maker(username):
    exists = cache.get("m::{}".format(username))
    if exists is None:
    
        url = "https://api.getmakerlog.com/users/{}/"
        r = requests.get(url.format(username))
        flag = False
        if r.status_code == requests.codes.ok:
            flag = True
        cache.set("m::{}".format(username), flag, timeout=60*60*24)
        return flag
    else:
        return exists
    
def post_vote_count(id):
    exists = cache.get("m::{}".format(id))
    if exists is None:
        url = "https://api.producthunt.com/v1/posts/{}"
        r = requests.get(url.format(id), headers=h)
        resp = r.json().get("post").get("votes_count")
        cache.get("m::{}".format(id), resp)
        return resp
    else:
        return exists



def votes(id,uid):
    l = []
    page = 1
    count = 0
    percent_total = post_vote_count(id)
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
            cache.set(uid, count/percent_total*100)
    return count, l

def search(url_search, uid):
    import re
    exists = cache.get(url_search)
    if not exists is None:
        return exists
    else:
        content = requests.get(url_search).text
        resp = re.search('producthunt\:\/\/post\/(?P<id>[0-9]+)', content)
        if resp:
            id =  resp.groupdict().get("id")
            if id:
                res=votes(id, uid)
                cache.set(url_search, res, timeout=60*30)
                return res