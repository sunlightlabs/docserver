from BeautifulSoup import BeautifulSoup, SoupStrainer
from docserver.public_site.models import Document, DocumentLegislation
from django.core.management.base import NoArgsCommand
from scrape_utils import *
import datetime, time
import feedparser
import urllib2

def split_title(title):
    title_arr = title.split(',', 1)
    title_dict = {"gov_id":title_arr[0], "title":title_arr[1].strip()}
    return title_dict

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        doc_type = "OMB Memo"
        file_type = "pdf"
        add_date = datetime.datetime.now()
        d = feedparser.parse("http://www.whitehouse.gov/omb/assets/rss/ombmemos.xml")
        
        for entry in d.entries:
            title_dict = split_title(entry.title)
            gov_id = title_dict['gov_id']
            release_date = entry.updated_parsed
            release_date=datetime.datetime(release_date[0], release_date[1], release_date[2])
            title = title_dict['title']
            description = entry.description
            original_url = entry.link
    
            matches = Document.objects.filter(doc_type=doc_type, gov_id=gov_id, release_date=release_date)
            if len(matches) == 0:
                if gov_id:
                    local_file = archive_file(original_url, gov_id, doc_type, file_type)
                    doc = Document(gov_id=gov_id, release_date=release_date, add_date=add_date, title=title, description=description, doc_type=doc_type, original_url=original_url, local_file=local_file)
                    doc.save()