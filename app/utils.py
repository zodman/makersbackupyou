import requests
import pprint
h = {
    "Authorization": "Bearer 7112d23e618e967f9475ce6d28a391e50d7ff6924bec1c400ae9a13122d6eede"
}

def votes(id):
    l = []
    page = 1
    while True:
        url ="https://api.producthunt.com/v1/posts/{}/votes?page={}"
        r =requests.get(url.format(id,page), headers=h)
        response = r.json()
        page +=1
        if not response.get("votes"):
            break
        for i in response.get("votes"):
            username = i.get("user").get("username")
            image = i.get("user").get("image_url").get("30px")
            name = i.get("user").get("name")
            l.append(dict(username=username, image=image, name=name))
    return l
def search(url_search):
    url ="https://api.producthunt.com/v1/posts/all?search[url]={}"
    r =requests.get(url.format(url_search), headers=h)
    response = r.json()
    pprint.pprint(response)
    l = []
    for post in response.get("posts"):
        name = post.get("name")
        id = post.get("id")
        thumbnail = post.get("thumbnail").get("image_url")
        l.append(dict(name=name, id=id, thumbnail=thumbnail))
    return l