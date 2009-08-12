from django.core.management.base import NoArgsCommand
from docserver.public_site.models import Document
import feedparser
import datetime, time
from string import strip

#extract document id from url
def extract_id(url):
    url_arr = url.split('/')
    session = url_arr[len(url_arr) - 2]
    file_name = url_arr[len(url_arr) - 1]
    gov_id = "%s-%s" % (session, file_name)
    gov_id = gov_id.replace('.pdf', '').upper()
    return gov_id

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        d = feedparser.parse("http://www.whitehouse.gov/omb/assets/rss/ombsaps.xml")
        
        for entry in d.entries:
            release_date = entry.updated_parsed
            release_date=datetime.datetime(release_date[0], release_date[1], release_date[2])
            add_date = datetime.datetime.now()
            title = entry.title
            description = entry.description
            doc_type = "OMB SAP"
            original_url = entry.link
            gov_id = extract_id(entry.link)
            local_file = ""
    
            matches = Document.objects.filter(doc_type=doc_type, gov_id=gov_id, release_date=release_date)
            if len(matches) > 0:
                pass
            else:
                if gov_id != "-":
                    doc = Document(gov_id=gov_id, release_date=release_date, add_date=add_date, 
			title=title, description=description, doc_type=doc_type, original_url=original_url, 
			local_file=local_file)
                    doc.save()
                    None
