from django.core.management.base import NoArgsCommand
import feedparser
import datetime, time
from docserver.public_site.models import Document
import urllib2

def split_title(title):
    title_arr = title.split(',', 1)
    title_dict = {"gov_id":title_arr[0], "title":title_arr[1].strip()}
    return title_dict

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        d = feedparser.parse("http://www.whitehouse.gov/omb/assets/rss/ombmemos.xml")
        
        for entry in d.entries:
            title_dict = split_title(entry.title)
            gov_id = title_dict['gov_id']
            release_date = entry.updated_parsed
            release_date=datetime.datetime(release_date[0], release_date[1], release_date[2])
            add_date = datetime.datetime.now()
            title = title_dict['title']
            description = entry.description
            doc_type = "OMB Memo"
            original_url = entry.link
            local_file = ""
    
            matches = Document.objects.filter(doc_type=doc_type, gov_id=gov_id, release_date=release_date)
            if len(matches) > 0:
                pass
            else:
                if gov_id != None:
                    try:
                        file_name = "/var/www/data/docserver/omb_memo/%s.pdf" % gov_id
                        remote_file = urllib2.urlopen(original_url)
                        local_file = open(file_name, "w")
                        local_file.write(remote_file.read())
                        local_file.close
                    except:
                        print "nope"
                    doc = Document(gov_id=gov_id, release_date=release_date, add_date=add_date, title=title, description=description, doc_type=doc_type, original_url=original_url, local_file=local_file)
                    doc.save()