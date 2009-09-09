from BeautifulSoup import BeautifulStoneSoup
from docserver.public_site.models import Document
from django.core.management.base import NoArgsCommand
from scrape_utils import *
import datetime
import urllib2

class Command(NoArgsCommand):
    
    
    def handle_noargs(self, **options):
        add_date=datetime.datetime.now()
        OPEN_CRS_KEY = '***REMOVED***'
        doc_type = "CRS"
        file_type = "pdf"
        
        for i in range(2,50):
            print "PAGE %s" % i
            url = "http://opencrs.com/recent/feed.xml?key=%s&page=%s" % (OPEN_CRS_KEY, i)
            print url
            page = urllib2.urlopen(url)
            soup = BeautifulStoneSoup(page)
            for document in soup.documents.findAll('document'):
                order_code = document['order_code']
                release_date = document['release_date']
                gov_id = "CRS_%s_%s" % (order_code, release_date.replace('-', ''))
                title = document.title.contents[0]
                description = ' '
                original_url = document.locations.findAll('location')[0]['url']
                matches = Document.objects.filter(doc_type=doc_type, gov_id=gov_id, release_date=release_date)
                if not matches:
                    if gov_id:
                        local_file = archive_file(original_url, gov_id, doc_type, file_type)
                        full_text = pdf_extract_text(local_file, original_url)
                        doc = Document(gov_id=gov_id, release_date=release_date, add_date=add_date, title=title, 
                            description=description, doc_type=doc_type, original_url=original_url, 
                            local_file=local_file, full_text=full_text)
                        doc.save()
                print gov_id