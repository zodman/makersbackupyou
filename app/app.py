from django_micro import configure, route, run
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib import messages
from django import forms
from utils import search as search_url
from utils import votes
DEBUG = True
INSTALLED_APPS= [ "widget_tweaks",]
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

configure(locals())
from django.views.decorators.cache import cache_page


class FUrl(forms.Form):
    url = forms.CharField()

    def search(self):
        url =self.cleaned_data.get("url")
        return search_url(url)

@route('', name='homepage')
def homepage(request):
    context = dict()
    context["form"] = FUrl()
    if request.method == "POST":
        f = FUrl(request.POST)
        context["form"] = f
        if f.is_valid():
            id = f.search()
            if id:
                total, result = votes(id)
                context["votes"] = dict(total=total, result=result)
            else:
                context["error"]= "Url not found on producthunt.com"
        else:
            context["erro"]= "Form invalid"

    return render(request, "home.html", context)

application = run()
