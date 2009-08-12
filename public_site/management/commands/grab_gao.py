from django.core.management.base import NoArgsCommand
from docserver.public_site.models import Document
from scrape_utils import *
import datetime, time
import feedparser

def split_title(title):
    title_arr_small = title.split(',', 1)
    title_arr_big = title.split(',')
    date_str = "%s, %s" % (title_arr_big[len(title_arr_big) - 2].strip(), title_arr_big[len(title_arr_big) - 1].strip())
    title = title_arr_small[1].replace(date_str, '').rstrip().rstrip(',')
    title_dict = {"gov_id":title_arr_small[0], "title":title.strip()}
    return title_dict

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        doc_type = "GAO"
        d = feedparser.parse("http://www.gao.gov/rss/reports.xml")
        
        for entry in d.entries:
            title_dict = split_title(entry.title)
            gov_id = title_dict['gov_id']
            release_date = entry.updated_parsed
            release_date=datetime.datetime(release_date[0], release_date[1], release_date[2])
            add_date = datetime.datetime.now()
            title = title_dict['title']
            description = entry.description
            original_url = entry.link
            local_file = ""
    
            matches = Document.objects.filter(doc_type=doc_type, gov_id=gov_id, release_date=release_date)
            if len(matches) > 0:
                pass
            else:
                if gov_id != None:
                    archive_file(original_url, gov_id, doc_type, file_type)
                    doc = Document(gov_id=gov_id, release_date=release_date, add_date=add_date, title=title, 
                        description=description, doc_type=doc_type, original_url=original_url, local_file=local_file)
                    doc.save()