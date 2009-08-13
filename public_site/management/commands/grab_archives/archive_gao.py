from django.core.management.base import NoArgsCommand
import feedparser
import datetime, time
from docserver.public_site.models import Document
import urllib2

class Command(NoArgsCommand):
    
    def handle_noargs(self,  **options):
        docs = Document.objects.filter(doc_type='GAO')
        for doc in docs:
            original_url = doc.original_url
            gov_id = doc.gov_id
            try:
                file_name = "/var/www/data/docserver/gao/%s.pdf" % gov_id
                remote_file = urllib2.urlopen(original_url)
                local_file = open(file_name, "w")
                local_file.write(remote_file.read())
                local_file.close
                print gov_id
            except:
                print "nope"
            time.sleep(.5)