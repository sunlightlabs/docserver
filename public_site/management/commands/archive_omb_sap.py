from BeautifulSoup import BeautifulSoup, SoupStrainer
from congress_utils import *
from docserver.public_site.models import Document, DocumentLegislation
from django.core.management.base import NoArgsCommand
from scrape_utils import *
from time import sleep
import datetime, time
import urllib2

class Command(NoArgsCommand):
    # grabs a session of OMB statements of administration policy and saves them to db
    # format works from 108th congress through 110th congress
    # 111th congress has new format and will not work with this script
    def handle_noargs(self, **options):
        file_type="pdf"
        congress = 110
        session = 2
        url_prefix = "http://georgewbush-whitehouse.archives.gov/omb/legislative/sap/%s-%s/" % (congress, session)
        url = "%sindex-date.html" % url_prefix
        print url
        doc_type = "OMB SAP"
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page)

    	rpts = soup.findAll('table', width='465')[1].findAll('tr')
    	for report_row in rpts:       
    	    gov_id = None     
            cols = report_row.findAll('td')
            if len(cols) > 0:
                try:
                    file_name = cols[0].find('a')['href']
                    original_url = "%s%s" % (url_prefix, file_name)
                    gov_id = "%s-%s-%s" % (congress, session, file_name.replace('.pdf', '').upper())
                except:
                    original_url = None
                    gov_id = None
                    
                try:
                    bill_num = cols[0].find('a').string.replace('H ', 'H.').replace('HR ', 'H.R.').replace('S ', 'S.').replace('SJR ', 'S.J.Res.')
                    bill_num = bill_num.replace(' ', '').replace('\r\n', '')
                except:
                    bill_num = None
                    
                try:
                    title = cols[1].contents[0].strip().replace('\r\n', '')
                except:
                    title = ''
                    
                try:
                    date_str = cols[2].string
                    release_date = time.strftime('%Y-%m-%d', time.strptime(date_str, '%m/%d/%Y'))
                except:
                    release_date = None
                    
                try:
                    recipient = cols[3].string
                except:
                    recipient = None
                
                add_date = datetime.datetime.now()
                description = ''
                local_file = ''
            
            if gov_id:	                
                matches = Document.objects.filter(doc_type=doc_type, gov_id=gov_id, release_date=release_date)
                if matches:
                    doc = matches[0]
                    if bill_num:
                        bill_num = clean_bill_num(bill_num)
                        bill_dupe = DocumentLegislation.objects.filter(congress=congress).filter(bill_num=bill_num).filter(document=doc)
                        if not bill_dupe:
                            bill = DocumentLegislation(congress=congress, bill_num=bill_num, document=doc)
                            bill.save()
                        else: 
                            print "bill dupe"
                else:
                    #local_file = archive_file(original_url, gov_id, doc_type, file_type)
                    #time.sleep(1)   
                    full_text = pdf_extract_text(local_file, original_url)
                    doc = Document(gov_id=gov_id, release_date=release_date, add_date=add_date, title=title, 
                        description=description, doc_type=doc_type, original_url=original_url, 
                        local_file=local_file, full_text=full_text)
                    doc.save()
                    if bill_num:
                        bill_num = clean_bill_num(bill_num)
                        bill_dupe = DocumentLegislation.objects.filter(congress=congress).filter(bill_num=bill_num).filter(document=doc)
                        if not bill_dupe:
                            bill = DocumentLegislation(congress=congress, bill_num=bill_num, document=doc)
                            bill.save()
                        else: 
                            print "bill dupe"
                    print "added %s: %s" % (gov_id, bill_num)