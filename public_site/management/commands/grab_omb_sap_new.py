from django.core.management.base import NoArgsCommand
import datetime, time
import urllib2
from BeautifulSoup import BeautifulSoup, SoupStrainer
from docserver.public_site.models import Document, DocumentLegislation
import re

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        
        # return list of bill numbers extracted from string
        def extract_legislation(haystack):
            haystack = haystack.upper()
            p = re.compile('S\.\s?CON\.\s?RES\.\s?\d{1,5}|H\.\s?CON\s?RES\.\s?\d{1,5}|S\.\s?J\.\s?RES\.\s\d{1,5}|H\.\s?J\.\s?RES\.\s\d{1,5}|S\.\s?RES\.\s?\d{1,5}|H\.\s?RES\.\s?\d{1,5}|H\.\s?\R\.\s?\d{1,5}|S\.\s?\d{1,5}')
            needle_list = p.findall(haystack)
            return needle_list
            
        #returns number of Congress in session for provided year
        def congress_from_year(year):
            if year < 1789:
                return None
            else:
                return int((year-1789)/2) + 1
        
        #returns session number of Congress for a provided year        
        def session_from_year(year):
            return 2 - (year % 2)
        
        base_url = "http://whitehouse.gov"
        add_date = datetime.datetime.now()
        doc_type = "OMB SAP"
        page = urllib2.urlopen("http://www.whitehouse.gov/omb/111/legislative_sap_date/")
        soup = BeautifulSoup(page)
        link = soup.find('a', href=re.compile('asset.aspx'))
        rows = link.parent.parent.parent.parent.findAll('tr')
        for row in rows:
            cols = row.findAll('td')
            if cols:
                #print cols
                bill = cols[0].find('a').string.replace('&nbsp;', ' ').replace('S ', 'S.').replace('HR ', 'H.R.').replace(' ', '')
                clean_bill = bill.replace('.', '').replace(' ', '')
                original_url = "%s%s" % (base_url, cols[0].find('a')['href'])
                title = cols[1].contents[0].replace('&nbsp;', ' ').strip()
                date_str = cols[2].string.replace('&nbsp;', ' ')
                try:
                    release_date = time.strftime('%Y-%m-%d', time.strptime(date_str, '%B %d, %Y'))
                except:
                    release_date = None
                year = time.strptime(date_str, '%B %d, %Y')[0]
                congress = congress_from_year(year)
                session = session_from_year(year)
                recipient = cols[3].string
                bill_list = [bill]
                description = ""
                local_file = ""
                suffix = recipient[0]
                gov_id = "%s-%s-SAP%s-%s" % (congress, session, clean_bill, suffix)
                print gov_id
                
                matches = Document.objects.filter(doc_type=doc_type, gov_id=gov_id, release_date=release_date)
                if len(matches) > 0:
                    pass
                else:
                    if gov_id != None:
                        try:
                            file_name = "/var/www/data/docserver/omb_sap/%s.pdf" % gov_id
                            remote_file = urllib2.urlopen(original_url)
                            local_file = open(file_name, "w")
                            local_file.write(remote_file.read())
                            local_file.close
                        except:
                            print "nope"
                        doc = Document(gov_id=gov_id, release_date=release_date, add_date=add_date, title=title, 
                            description=description, doc_type=doc_type, original_url=original_url, local_file=local_file)
                        doc.save()

                        for bill in bill_list:
                            bill_num = bill.replace(' ', '')
                            bill = DocumentLegislation(congress=congress, bill_num=bill_num, document=doc)
                            bill.save()