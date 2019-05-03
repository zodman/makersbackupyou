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
SESSION_ENGINE= "django.contrib.sessions.backends.signed_cookies" 
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
    from django_rq.utils import get_statistics
    import redis
    job_id = request.session.get("job")
    context = {'percent': 0}
    status = ""
    if job_id:
        try:
            job = rq.job.Job.fetch(job_id, connection=redis.Redis())
            status = job.get_status()
            context["url"] = job.args[0]
        except rq.exceptions.NoSuchJobError:
            pass

        context["status"] = status
        percent = cache.get(request.session.get("uid", 0))
        context["percent"] = percent
        if status == "finished":
            res = job.result
            context["votes"]  = dict(total=res[0], result=res[1])

    context["stat"] = get_statistics()
    return render(request, "votes.html", context)


@route('', name='home')
def homepage(request):
    context = dict()
    context["form"] = FUrl()
    if request.method == "POST":
        f = FUrl(request.POST)
        context["form"] = f
        if f.is_valid():
            url = f.cleaned_data.get("url")
            uid = str(uuid.uuid4())
            cache.set(uid, 0)
            job = django_rq.enqueue(search_url, url, uid)
            request.session["uid"] = uid
            request.session["job"] = job.get_id()
    return render(request, "home.html", context)


application = run()
