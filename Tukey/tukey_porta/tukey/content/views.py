import re, os,requests
from tukey.content.models import Page
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext 
from django.utils.safestring import mark_safe
from horizon.decorators import require_auth, require_perms

from .forms import PageForm

def page(request, slug=''):
    #slug can either be blank or contain \w and -, safe because from urls.py regex
    #test index page
    #nav_pages = Page.objects.order_by('nav_order')
    if slug=="":
        return render(request,'newIndex.html',{'rss_category': None})
    p = get_object_or_404(Page, pk=slug)
    p=""
    page = slug+".html"
    return render(request, 'content/page.html', {'content' : p, 'page':page})

def publications(request):
    page='publications.html'
    try:
        response=requests.get(settings.PUBLICATION_URL)
        text=u'<ul' + response.text.split(u'<ul')[1]  
        text=text.replace(u'</body></html>','')
    except Exception as e:
        text=str(e)
    return render(request,'content/page.html',{'content':text,'page':page})

@require_auth
def content_admin(request):
    if request.user.has_perm("openstack.roles.tukeycontentadmin"):
        pages = Page.objects.order_by('slug')
        content_pages = []
        non_content_pages = []
        for page in pages:
            #hackity hack hack
            if page.content == '':
                non_content_pages.append(page)
            else:
                content_pages.append(page)
                
        return render(request, 'content/admin.html', {'content_pages' : content_pages, 
            'non_content_pages' : non_content_pages})
    else:
        return HttpResponseRedirect("/")

def page_edit(request, slug=''):
    page = get_object_or_404(Page, pk=slug)

    if request.method == 'POST':
        form = PageForm(request.POST, instance=page)
        if form.is_valid():
            form.save()
            return redirect("/content-admin")
    else:
        form = PageForm(instance=page) # An unbound form

    return render(request, 'content/edit.html', {
        'form': form,
        'page': page,
    })

def page_add(request):
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/content-admin")
    else:
        form = PageForm() # An unbound form

    return render(request, 'content/add.html', {
        'form': form,
    })

def page_delete(request, slug='', confirm=None):
    page = get_object_or_404(Page, pk=slug)
    if not confirm:
        return render(request, 'content/delete.html', {'page' : page})
    if confirm == "YES":
        page.delete()
        return redirect("/content-admin")


def rss_page(request):
    return render(request, 'content/news.html', {'rss_category': None})
    
