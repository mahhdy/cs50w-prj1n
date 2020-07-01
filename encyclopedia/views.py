import random
import re

from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from markdown2 import Markdown
from . import util


markdowner = Markdown()


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def load_page(request, title):
    entry = util.get_entry(title)
    if entry:
        body = markdowner.convert(entry)
        check = re.match(r'<h1>([^<>]*)</h1>', body)
        title = check.group(1) if check else ''
        return render(request, 'encyclopedia/entry.html', {'entry': body, 'title': title})
    raise Http404("Entry does not exist")


def search(request):
    q = request.GET.get('q')
    check = util.get_entry(q)
    if check:
        return HttpResponseRedirect(reverse_lazy('load_page', args=[q]))
    all = util.list_entries()
    if any(q.upper() in s.upper() for s in all):

        return render(request, "encyclopedia/result.html", {"entries": [s for s in all if q.upper() in s.upper()]})
    messages.error(request, f'No matching entries was found for {q} !')
    return HttpResponseRedirect("/")


def random_page(request):
    all = util.list_entries()
    i = random.randint(0, len(all)-1)
    return HttpResponseRedirect(reverse_lazy('load_page', args=[all[i]]))


def create_page(request):
    if request.method == 'POST':
        title = request.POST.get('title').strip()
        entry = request.POST.get('body').strip()
        all = util.list_entries()
        if title.lower() in (a.lower() for a in all):
            messages.error(request, f'Another Entry with the name of {title} exist!')
            return render(request, 'encyclopedia/create.html', {'title': title, 'body': entry})
        else:
            entry = f'# {title}\n\n {entry}'
            util.save_entry(title, entry)
            return HttpResponseRedirect(reverse_lazy('load_page', args=[title]))
    return render(request, 'encyclopedia/create.html')


def edit_page(request, title):
    entry = util.get_entry(title)
    if entry:
        if request.method == 'POST':
            entry = request.POST.get('body').strip()
            if len(entry) > 10:
                util.save_entry(title, entry)
                return HttpResponseRedirect(reverse_lazy('load_page', args=[title]))
            else:
                messages.error(request, f'New Entry Don\'t have enough characters!')
        return render(request, 'encyclopedia/edit.html', {'body': entry, 'title': title})
    raise Http404("Entry does not exist")