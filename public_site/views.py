from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.core.paginator import Paginator
from docserver.public_site.models import Document, DocumentLegislation, Vote, Action
from django.db.models import Count
from django.views.generic import list_detail
import mimetypes
import re

FRIENDLY_MAP = {'hr':'H.R.', 'hres':'H.RES.', 's':'S.', 'sres':'S.R.', 'hconres':'H.CON.RES.', 
    'sconres':'S.CON.RES', 'hjres':'H.J.RES', 'sjres':'S.J.RES.'}

GT_MAP = {'hr':'h', 'hres':'hr', 's':'s', 'sres':'sr'}

DOC_TYPE_MAP = {'cbo':'CBO CE', 'gao':'GAO', 'rpc':'RPC LN', 'dpc':'DPC LB', 'omb':'OMB Memo', 'srp':'RCR SRP', 'jct':'JCT', 'crs':'CRS', 'sap':'OMB SAP'}

TYPE_NAME_MAP = {'cbo':'CBO Cost Estimates', 'gao':'GAO Reports',
                    'rpc':'Republican Policy Committee Legislative Notices',
                    'dpc':'Democratic Policy Committee Legislative Briefs',
                    'omb':'OMB Memos', 'sap':'Statements of Administration Policy',
                    'srp':'Statements of Republican Policy',
                    'jct':'Joint Committee on Taxation Reports'}
                    
RESULTS_PER_PAGE = 20
                    
def index(request):
    docs =  Document.objects.all().order_by('-release_date')[:20]
    recent = DocumentLegislation.objects.top_recent(90, 30)
    new_recent = DocumentLegislation.objects.aggregate(doc_count=Count('document', distinct=True))
    link_list = []
    for k in TYPE_NAME_MAP:
        link_list.append((k, TYPE_NAME_MAP[k]))
    return render_to_response('public_site/index.html', {"link_list":link_list, "doc_list":docs, "recent_list":recent})
    
def search(request):
    if 'q' in request.GET:
        query = request.GET['q']
        document_list = Document.search.query(query)
        paginator = Paginator(document_list, RESULTS_PER_PAGE)
        
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
        
    return render_to_response('public_site/search.html', {'results':documents, 'query':query})

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
    

def bill(request, congress, bill_type, bill_id, format='html'):
    bill_num = "%s%s" % (FRIENDLY_MAP[bill_type], bill_id)
    results = Document.objects.filter(documentlegislation__congress=congress).filter(documentlegislation__bill_num=bill_num).order_by('-release_date')
    template_name = 'public_site/list.%s' % format
    file_type = mimetypes.guess_type(template_name)[0]
    #return render_to_response('public_site/bill.html', {'results':results, 'bill':{'bill_num':bill_num, 'congress':congress}})
    return list_detail.object_list(request, queryset=results, template_object_name='document', template_name=template_name, mimetype=file_type,
        paginate_by=10, extra_context={'title':'Congress %s, %s' % (congress, bill_num)})
    

def typelist(request, doc_type, format='html'):
    results = Document.objects.filter(doc_type=DOC_TYPE_MAP[doc_type]).order_by('-release_date')
    template_name = 'public_site/list.%s' % format
    file_type = mimetypes.guess_type(template_name)[0]
    return list_detail.object_list(request, queryset=results, template_object_name='document', template_name=template_name, mimetype=file_type,
        paginate_by=10, extra_context={'title':TYPE_NAME_MAP[doc_type]})