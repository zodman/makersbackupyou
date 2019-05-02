from django_micro import configure, route, run
from django.http import HttpResponse
from django.shortcuts import render
from django import forms
from utils import search as search_url
from utils import votes
DEBUG = True
INSTALLED_APPS= [ "widget_tweaks",]
configure(locals())


class FUrl(forms.Form):
    url = forms.CharField()

    def search(self):
        url =self.cleaned_data.get("url")
        return search_url(url)

@route('', name='homepage')
def homepage(request):
    context = dict()
    context["form"] = FUrl()
    if request.method=="POST":
        f = FUrl(request.POST)
        if f.is_valid():
            context["result"] = f.search()


    id = request.GET.get("id")
    if id:
        result = votes(id)
        context["votes"] = result

    return render(request, "home.html", context)

application = run()
