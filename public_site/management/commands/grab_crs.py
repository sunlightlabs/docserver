from django.core.management.base import NoArgsCommand
import feedparser
import datetime, time
from docserver.public_site.models import Document

def split_title(title):
    title_arr = title.split(',', 1)
    title_dict = {"gov_id":title_arr[0], "title":title_arr[1].strip()}
    return title_dict

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        d = feedparser.parse("http://opencrs.com/syndication/recentpdf.rss")
        
        for entry in d.entries:
            print entry
            
            title_dict = split_title(entry.title)
            gov_id = title_dict['gov_id']
            release_date = entry.updated_parsed
            release_date=datetime.datetime(release_date[0], release_date[1], release_date[2])
            add_date = datetime.datetime.now()
            title = title_dict['title']
            description = ""
            doc_type = "CRS"
            original_url = entry.link
            local_file = ""
    
            matches = Document.objects.filter(doc_type=doc_type, gov_id=gov_id, release_date=release_date)
            if len(matches) > 0:
                pass
            else:
                doc = Document(gov_id=gov_id, release_date=release_date, add_date=add_date, title=title, description=description, doc_type=doc_type, original_url=original_url, local_file=local_file)
                print doc
                doc.save()