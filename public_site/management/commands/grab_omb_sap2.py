from BeautifulSoup import BeautifulSoup, SoupStrainer
from public_site.models import Document, DocumentLegislation
from django.core.management.base import NoArgsCommand
from scrape_utils import *
from congress_utils import congress_from_year, session_from_year, current_congress_session
import datetime, time
import urllib2
import re

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        doc_type = "OMB SAP"
        file_type = "pdf"
        base_url = "http://whitehouse.gov"
        current_congress = current_congress_session()['congress']
        page = urllib2.urlopen("http://www.whitehouse.gov/omb/%s/legislative_sap_date_%s" % (current_congress, datetime.datetime.now().year))
        add_date = datetime.datetime.now()
        
        soup = BeautifulSoup(page)
        link = soup.find('a', href=re.compile('.pdf'))
        rows = link.parent.parent.parent.parent.findAll('tr')
        for row in rows:
            cols = row.findAll('td')
            if cols:
                bill = cols[0].find('a').string.replace('&nbsp;', ' ').replace('S ', 'S.').replace('HR ', 'H.R.').replace(' ', '')
                clean_bill = bill.replace('.', '').replace(' ', '')
                original_url = "%s%s" % (base_url, cols[0].find('a')['href'])
                title = cols[1].contents[0].replace('&nbsp;', ' ').strip()
                date_str = cols[2].string.replace('&nbsp;', ' ').strip()
                try:
                    release_date = time.strftime('%Y-%m-%d', time.strptime(date_str, '%B %d, %Y'))
                except:
                    release_date = None
                year = time.strptime(date_str, '%B %d, %Y')[0]
                congress = congress_from_year(year)
                session = session_from_year(year)
                recipient = cols[3].string.strip().replace('&nbsp;', ' ')
                bill_list = [bill]
                description = ""
                local_file = ""
                suffix = release_date
                gov_id = "%s-%s-SAP%s-%s" % (congress, session, clean_bill, suffix)
                
                matches = Document.objects.filter(doc_type=doc_type, gov_id=gov_id, release_date=release_date)
                if len(matches) == 0:
                    if gov_id:
                        print release_date
                        local_file = archive_file(original_url, gov_id, doc_type, file_type)
                        #full_text = pdf_extract_text(local_file, original_url)
                        full_text = None
                        doc = Document(gov_id=gov_id, release_date=release_date, add_date=add_date, title=title, 
                            description=description, doc_type=doc_type, original_url=original_url, 
                            local_file=local_file, full_text=full_text)
                        doc.save()
                        for bill_num in bill_list:
                            bill_dupe = DocumentLegislation.objects.filter(congress=congress).filter(bill_num=bill_num).filter(document=doc)
                            if not bill_dupe:
                                bill = DocumentLegislation(congress=congress, bill_num=bill_num, document=doc)
                                bill.save()