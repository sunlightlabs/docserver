from BeautifulSoup import BeautifulStoneSoup
from docserver.public_site.models import Document, DocumentLegislation
from django.core.management.base import NoArgsCommand
from django import db
from scrape_utils import *
import datetime
import urllib2

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        add_date=datetime.datetime.now()
        OPEN_CRS_KEY = '***REMOVED***'
        doc_type = "CRS"
        file_type = "pdf"
        
        for i in range(0,1):
            print "PAGE %s" % i
            url = "http://opencrs.com/recent/feed.xml?key=%s&page=%s" % (OPEN_CRS_KEY, i)
            print url
            page = urllib2.urlopen(url)
            soup = BeautifulStoneSoup(page)
            for document in soup.documents.findAll('document'):
                db.reset_queries()
                order_code = document['order_code']
                release_date = document['release_date']
                print order_code
                gov_id = "CRS_%s_%s" % (order_code, release_date.replace('-', ''))
                title = document.title.contents[0]
                description = ' '
                try:
                    original_url = document.locations.findAll('location')[0]['url']
                    bill_list = []
                    for bill in document.legislation.findAll('bill'):
                        bill_list.append({'bill_id':bill['id'], 'congress':bill['congress']})
                    matches = Document.objects.filter(doc_type=doc_type, gov_id=gov_id, release_date=release_date)
                    if not matches:
                        print "new"
                        if gov_id:
                            local_file = archive_file(original_url, gov_id, doc_type, file_type)
                            full_text = pdf_extract_text(local_file, original_url)
                            doc = Document(gov_id=gov_id, release_date=release_date, add_date=add_date, title=title, 
                                description=description, doc_type=doc_type, original_url=original_url, 
                                local_file=local_file, full_text=full_text)
                            doc.save()
                            for bill in bill_list:
                                bill_dupe = DocumentLegislation.objects.filter(congress=bill['congress']).filter(bill_num=bill['bill_id']).filter(document=doc)
                                if not bill_dupe:
                                    bill = DocumentLegislation(congress=bill['congress'], bill_num=bill['bill_id'], document=doc)
                                    bill.save()
                    else:
                        print "dupe"
                        doc = matches[0]
                        for bill in bill_list:
                            bill_dupe = DocumentLegislation.objects.filter(congress=bill['congress']).filter(bill_num=bill['bill_id']).filter(document=doc)
                            if not bill_dupe:
                                print "add bill %s" % bill
                                bill = DocumentLegislation(congress=bill['congress'], bill_num=bill['bill_id'], document=doc)
                                bill.save()
                except:
                    pass
                print gov_id
