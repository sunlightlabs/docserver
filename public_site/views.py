from congress_utils import *
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from public_site.models import Document, DocumentLegislation, Vote, Action
from django.db.models import Count
from django.views.decorators.cache import cache_page
from django.views.generic import list_detail
import congress_utils
import mimetypes
import re

from utils import *

def get_mime(format):
    if format=="json":
        mime_type = 'application/json'
    elif format=="xml":
        mime_type = 'text/xml'
    else:
        mime_type = 'text/html'
    return mime_type

@cache_page(60 * 60)              
def index(request):
    docs =  Document.objects.defer("full_text").order_by('-release_date')[:20]
    link_list = []
    for k in TYPE_NAME_MAP:
        link_list.append((k, TYPE_NAME_MAP[k]))
    return render_to_response('public_site/index.html', {"link_list":link_list, "doc_list":docs})

@cache_page(60*60)
def search(request, format='html'):
    if 'q' in request.GET:
        query = request.GET['q']
        document_list = Document.search.query(query)
        paginator = Paginator(document_list, 20)
        
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1

        try:
            documents = paginator.page(page)
        except (EmptyPage, InvalidPage):
            documents = paginator.page(paginator.num_pages)
    else:
        query = None
        documents = None
        
    return render_to_response('public_site/search.html', {'results':documents, 'query':query}, mimetype=get_mime(format))

@cache_page(60 * 60)
def timeline(request, congress, bill_type, bill_id):
    timeline = {}
    timeline_list = []
    
    bill_num = "%s%s" % (FRIENDLY_MAP[bill_type], bill_id)
    gt_num = "%s%s" % (GT_MAP[bill_type], bill_id)

    docs = DocumentLegislation.objects.filter(congress=congress)\
        .filter(bill_num=bill_num).order_by('document__release_date')
    for doc in docs:
        timeline[doc.document.release_date] = {'type':'Document', 'title':doc.document.title}
    
    votes = Vote.objects.filter(congress=congress).filter(issue=bill_num.replace('.', '')).order_by('date')
    for vote in votes:
        timeline[vote.date] = {'type':Vote, 'title':vote.title}
        
    actions = Action.objects.filter(congress=congress).filter(bill_num=gt_num).order_by('date')
    for action in actions:
        timeline[action.date] = {'type':'Action', 'description':action.description}
        
    keys = timeline.keys()
    keys.sort()
    for key in keys:
        timeline_list.append({'date':key, 'item':timeline[key]})

    return render_to_response('public_site/timeline.html', 
        {'bill_num':bill_num, 'congress':congress, 'timeline':timeline_list})
    
@cache_page(60 * 60)
def bill(request, congress, bill_type, bill_id, format='html'):
    bill_num = "%s%s" % (FRIENDLY_MAP[bill_type], bill_id)
    bill_identifier = "%s-%s-%s" % (congress, bill_type, bill_id)
    results = Document.objects.filter(documentlegislation__congress=congress).filter(documentlegislation__bill_num=bill_num).order_by('-release_date')
    template_name = 'public_site/list.%s' % format
    file_type = get_mime(format)
    return list_detail.object_list(request, queryset=results, template_object_name='document', template_name=template_name, mimetype=file_type,
        paginate_by=10, extra_context={'title':'Congress %s, %s' % (congress, bill_num), 'site': current_site(request), 'path': "bill/%s" % bill_identifier})
    
@cache_page(60 * 60)
def typelist(request, doc_type, format='html'):
    if "callback" in request.GET:
        callback = request.GET['callback']
    else:
        callback = None
    results = Document.objects.defer("full_text").filter(doc_type=DOC_TYPE_MAP[doc_type]).order_by('-release_date')
    template_name = 'public_site/list.%s' % format
    file_type = get_mime(format)
    return list_detail.object_list(request, queryset=results, template_object_name='document', template_name=template_name, mimetype=file_type,
        paginate_by=10, extra_context={'title':TYPE_NAME_MAP[doc_type], 'site':current_site(request), 'path': doc_type, 'callback':callback})
