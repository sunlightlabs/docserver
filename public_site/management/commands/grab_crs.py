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
        
        for i in range(1,2):
            url = "http://opencrs.com/api/reports/list.xml?key=%s&page=%s" % (OPEN_CRS_KEY, i)
            page = urllib2.urlopen(url)
            soup = BeautifulStoneSoup(page)
            for document in soup.response.findAll('resource'):
                db.reset_queries()
                order_code = document.find('ordercode').contents[0]
                release_date = document.find('releasedate').contents[0]
                original_url = document.find('download_url').contents[0]
                gov_id = "CRS_%s_%s" % (order_code, release_date.replace('-', ''))
                title = document.find('title').contents[0]
                description = ' '
                try:
                    matches = Document.objects.filter(doc_type=doc_type, gov_id=gov_id, release_date=release_date)
                    if not matches:
                        if gov_id:
                            local_file = archive_file(original_url, gov_id, doc_type, file_type)
                            full_text = pdf_extract_text(local_file, original_url)
                            doc = Document(gov_id=gov_id, release_date=release_date, add_date=add_date, title=title, 
                                description=description, doc_type=doc_type, original_url=original_url, 
                                local_file=local_file, full_text=full_text)
                            doc.save()
                    else:
                        pass
                except:
                    pass
                print gov_id
