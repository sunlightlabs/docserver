from BeautifulSoup import BeautifulSoup
from congress_utils import *
from docserver.public_site.models import Document, DocumentLegislation
from django.core.management.base import NoArgsCommand
from scrape_utils import *
import datetime, time
import urllib2

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        
        add_date = datetime.datetime.now()
        year = add_date.year
        doc_type = "DPC LB"
        file_type = "html"
        congress = congress_from_year(year)
        url_prefix = "http://dpc.senate.gov/"
        
        page = urllib2.urlopen("%sdpcreports.cfm?cf_year=%s&doctype=lb" % (url_prefix, year))
        soup = BeautifulSoup(page)
        
        rows = soup.findAll('p', { "class":"doclist" })
        for row in rows:
            file_name = row('a')[0]['href']
            gov_id = file_name.replace('dpcdoc.cfm?doc_name=', '').upper().strip()
            original_url = "%s%s" % (url_prefix, file_name)
            local_file = ''
            title = row('a')[0].string
            description = ''
            bill_list = extract_legislation(title)
            date_str = row.find('span', { "class":"doc-date" }).contents[0].replace('(', '').replace(')', '')
            release_date = time.strftime('%Y-%m-%d', time.strptime(date_str, '%m/%d/%y'))
               
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