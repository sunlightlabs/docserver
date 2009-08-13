from django.core.management.base import NoArgsCommand
from BeautifulSoup import BeautifulSoup
from congress_utils import *
from docserver.public_site.models import Document, DocumentLegislation
from scrape_utils import *
import datetime, time

class Command(NoArgsCommand):
        
    def handle_noargs(self, **options):
        
        add_date = datetime.datetime.now()
        doc_type = "CBO CE"
        url_prefix = "http://cbo.gov"
        file_type = "pdf"
        page = urllib2.urlopen("%s/search/ce_sitesearch.cfm" % url_prefix)
        soup = BeautifulSoup(page)
        items = soup('div', {'id':'res', 'class':'searchresults'})[0].findAll('p')
        for item in items:
            remote_file_name = item('a')[0]['href']
            original_url = "%s%s" % (url_prefix, remote_file_name)
            local_file = ''
            title = item('a')[0].string
            description = ''
            date_str = item.contents[2]
            release_date = time.strftime('%Y-%m-%d', time.strptime(date_str, '%B %d, %Y'))
            release_year = time.strptime(date_str, '%B %d, %Y')[0]
            congress = congress_from_year(release_year)
            bill_list = extract_legislation(title)
            if len(bill_list) > 0:
                bill_num = bill_list[0]
                gov_id = "%s-%s" % (congress, bill_num.replace('.', '').replace(' ', ''))
            else:
                bill_num = None
                gov_id = None
                              
            matches = Document.objects.filter(doc_type=doc_type, gov_id=gov_id, release_date=release_date)
            if len(matches) > 0:
                pass
            else:
                if gov_id != None:
                    archive_file(original_url, gov_id, doc_type, file_type)
                    doc = Document(gov_id=gov_id, release_date=release_date, add_date=add_date, title=title, 
                        description=description, doc_type=doc_type, original_url=original_url, local_file=local_file)
                    doc.save()
    
                    for bill in bill_list:
                        bill_num = bill.replace(' ', '')
                        bill = DocumentLegislation(congress=congress, bill_num=bill_num, document=doc)
                        bill.save()