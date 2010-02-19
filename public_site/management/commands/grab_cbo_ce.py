from public_site.congress_utils import extract_legislation, congress_from_year, clean_bill_num
from django.core.management.base import NoArgsCommand
from docserver.public_site.models import Document, DocumentLegislation
from scrape_utils import *
import datetime, time
import feedparser
import urllib2

def split_title(title):
    title_arr = title.split(',', 1)
    title_dict = {"gov_id":title_arr[0], "title":title.strip()}
    return title_dict

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        doc_type = "CBO CE"
        file_type = "pdf"
        d = feedparser.parse("http://www.cbo.gov/rss/latest10.xml")
        
        for entry in d.entries:
            title_dict = split_title(entry.title)
            release_date = entry.updated_parsed
            release_date=datetime.datetime(release_date[0], release_date[1], release_date[2])            
            congress = congress_from_year(release_date.year)
            add_date = datetime.datetime.now()
            title = title_dict['title']
            bill_list = extract_legislation(title)
            if len(bill_list) > 0:
                bill_num = bill_list[0]
                gov_id = "%s-%s" % (congress, bill_num.replace('.', '').replace(' ', ''))
            else:
                bill_num = None
                gov_id = None
            if 'description' in entry:
                description = entry.description
            original_url = entry.link

            matches = Document.objects.filter(doc_type=doc_type, gov_id=gov_id, release_date=release_date)
            if len(matches) == 0:
                if gov_id:
                    local_file = archive_file(original_url, gov_id, doc_type, file_type)
                    full_text = pdf_extract_text(local_file, original_url)
                    doc = Document(gov_id=gov_id, release_date=release_date, add_date=add_date, title=title, 
                        description=description, doc_type=doc_type, original_url=original_url, 
                        local_file=local_file, full_text=full_text)
                    doc.save()
                    for bill_num in bill_list:
                        bill_dupe = DocumentLegislation.objects.filter(congress=congress).filter(bill_num=bill_num).filter(document=doc)
                        if not bill_dupe:
                            bill = DocumentLegislation(congress=congress, bill_num=bill_num, document=doc)
                            bill.save()
