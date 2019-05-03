from django_micro import configure, route, run
import django_micro
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib import messages
from django import forms
from utils import search as search_url
from utils import votes
import django_rq
import uuid 
from django.core.cache import cache

DEBUG = True
INSTALLED_APPS= [ "widget_tweaks","django_rq"]
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
        'DEFAULT_TIMEOUT': 50000,
    }
}

configure(locals(), django_admin=True)
from django.views.decorators.cache import cache_page


class FUrl(forms.Form):
    url = forms.CharField()

    def clean_url(self):
        url = self.cleaned_data.get("url")
        if "producthunt.com/posts/" in url:
            return url
        raise forms.ValidationError("Not https://producthunt.com/posts/product url")

@route("status", name="status")
def status(request):
    import rq
    import redis
    job_id = request.session.get("job")
    if job_id:
        job = rq.Job.fetch(job_id, connection=redis.Redis())
        print(job.get_status())
    return render(request, "votes.html", {})


@route('', name='home')
def homepage(request):
    context = dict()
    context["form"] = FUrl()
    if request.method == "POST":
        f = FUrl(request.POST)
        context["form"] = f
        if f.is_valid():
            url  = f.cleaned_data.get("url")
            uid = uuid.uuid4()
            job = django_rq.enqueue(search_url, url, uid)
            request.session["job"] = job.get_id()
    return render(request, "home.html", context)


application = run()
