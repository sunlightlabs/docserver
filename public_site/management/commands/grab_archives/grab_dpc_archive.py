from django.core.management.base import NoArgsCommand
import datetime, time
import urllib2
from BeautifulSoup import BeautifulSoup
from docserver.public_site.models import Document, DocumentLegislation
import re

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        
        # return list of bill numbers extracted from string
        def extract_legislation(haystack):
            haystack = haystack.upper()
            print haystack
            p = re.compile('S\.\s?CON\.\s?RES\.\s?\d{1,5}|H\.\s?CON\s?RES\.\s?\d{1,5}|S\.\s?J\.\s?RES\.\s\d{1,5}|H\.\s?J\.\s?RES\.\s\d{1,5}|S\.\s?RES\.\s?\d{1,5}|H\.\s?RES\.\s?\d{1,5}|H\.\s?\R\.\s?\d{1,5}|S\.\s?\d{1,5}')
            needle_list = p.findall(haystack)
            return needle_list
            
        #returns number of Congress in session for provided year
        def congress_from_year(year):
            if year < 1789:
                return None
            else:
                return int((year-1789)/2) + 1
        
        add_date = datetime.datetime.now()
        doc_type = "DPC LB"
        year = 2007
        congress = congress_from_year(year)
        url_prefix = "http://dpc.senate.gov/"
        
        page = urllib2.urlopen("%sdpcreports.cfm?cf_year=%s&doctype=lb" % (url_prefix, year))
        soup = BeautifulSoup(page)
        
        rows = soup.findAll('p', { "class":"doclist" })
        for row in rows:
            file_name = row('a')[0]['href']
            gov_id = file_name.replace('dpcdoc.cfm?doc_name=', '').upper()
            original_url = "%s%s" % (url_prefix, file_name)
            local_file = ''
            title = row('a')[0].string
            description = ''
            bill_list = extract_legislation(title)
            date_str = row.contents[2].string.replace('(', '').replace(')', '')
            release_date = time.strftime('%Y-%m-%d', time.strptime(date_str, '%m/%d/%y'))
            
            print bill_list

            matches = Document.objects.filter(doc_type=doc_type, gov_id=gov_id, release_date=release_date)
            if len(matches) > 0:
                pass
            else:
                if gov_id != None:
                    doc = Document(gov_id=gov_id, release_date=release_date, add_date=add_date, title=title, 
                        description=description, doc_type=doc_type, original_url=original_url, local_file=local_file)
                    doc.save()
            
                    for bill in bill_list:
                        bill_num = bill.replace(' ', '')
                        bill = DocumentLegislation(congress=congress, bill_num=bill_num, document=doc)
                        bill.save()