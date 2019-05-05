import requests
from django.core.cache import cache
from memorised.decorators import memorise
import logging

log = logging.getLogger(__name__)

h = {
    "Authorization": "Bearer 7112d23e618e967f9475ce6d28a391e50d7ff6924bec1c400ae9a13122d6eede"
}

def _fetch_all_users():
    
    is_fetch = cache.get("::fetch..")
    if is_fetch is None:
        print(">>> fetch")
        url = "https://api.getmakerlog.com/users/?limit=5000"
        r = requests.get(url)
        json_r = r.json()
        #print(json_r)
        cache.set("::fetch..", json_r)
        return json_r
    else:
        return is_fetch


def check_maker(username):
    r = _fetch_all_users()
    for i in r.get("results"):
        if i.get("username") == username \
            or i.get("product_hunt_handle") == username:
            return True
    return False

@memorise(ttl=60*30)
def post_vote_count(id):
    print("...posts")
    url = "https://api.producthunt.com/v1/posts/{}"
    r = requests.get(url.format(id), headers=h)
    resp = r.json().get("post").get("votes_count")
    return resp

@memorise(ttl=60*30)
def _f(idd, ppage):
    print("..._f")
    url = "https://api.producthunt.com/v1/posts/{}/votes?page={}"
    r = requests.get(url.format(idd,ppage), headers=h)
    return r.json()

def votes(id,uid):
    l = []
    page = 1
    count = 20

    percent_total = post_vote_count(id)
    cache.set(uid, 15)
    while True:
        response = _f(id,page)
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
            percent = count/(percent_total-20)*100
            #print("percent {} for {} :: {}>{} {} {}".format(percent, id,uid, cache.get(uid), percent_total, count))
            cache.set(uid, percent)
    return count, l


def search(url_search, uid):
    import re
    cache.set(uid, 5)

    content = requests.get(url_search).text
    cache.set(uid, 10)
    resp = re.search('producthunt\:\/\/post\/(?P<id>[0-9]+)', content)
    if resp:
        id =  resp.groupdict().get("id")
        if id:
            log.info("votes for project id: {}".format(id))
            res=votes(id, uid)
            return res