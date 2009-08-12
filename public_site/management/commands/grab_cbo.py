from django.core.management.base import NoArgsCommand
import feedparser
import datetime, time
from docserver.public_site.models import Document
import urllib2

def split_title(title):
    title_arr = title.split(',', 1)
    title_dict = {"gov_id":title_arr[0], "title":title.strip()}
    return title_dict

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        d = feedparser.parse("http://www.cbo.gov/rss/latest10.xml")
        
        for entry in d.entries:
            title_dict = split_title(entry.title)
            gov_id = title_dict['gov_id']
            release_date = entry.updated_parsed
            release_date=datetime.datetime(release_date[0], release_date[1], release_date[2])
            add_date = datetime.datetime.now()
            title = title_dict['title']
            if 'description' in entry:
                description = entry.description
            doc_type = "CBO"
            original_url = entry.link
            #try:
            file_name = "/var/www/data/docserver/cbo_ce/%s.pdf" % gov_id
            remote_file = urllib2.urlopen(original_url)
            local_file = open(file_name, "w")
            local_file.write(remote_file.read())
            local_file.close
            #except:
            #    print "nope"
            local_file = ""
            print gov_id
    
            if False:
                matches = Document.objects.filter(doc_type=doc_type, gov_id=gov_id, release_date=release_date)
                if len(matches) > 0:
                    pass
                else:
                    doc = Document(gov_id=gov_id, release_date=release_date, add_date=add_date, 
			title=title, description=description, doc_type=doc_type, original_url=original_url, 
			local_file=local_file)
                    doc.save()
