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
        doc_type = "RCR SRP"
        year = 2009
        congress = congress_from_year(year)
        base_url = 'http://repcloakroom.house.gov/news/'
        
        page = urllib2.urlopen("http://repcloakroom.house.gov/news/DocumentQuery.aspx?DocumentTypeID=1501")
        soup = BeautifulSoup(page)
        
        rows = soup.findAll('span', { "class":"middlecopy" })
        for row in rows:
            if row.find('span', { "class":"middleheadline" }):
                title = str(row.find('span', { "class":"middleheadline" }).contents[1]).replace('<b>', '').replace('</b>', '').strip()
                bill_list = extract_legislation(title)
                date_str = row.find('span', { "class":"middleheadline" }).parent.contents[5].contents[0].replace('&nbsp;-', '').strip()
                release_date = time.strftime('%Y-%m-%d', time.strptime(date_str, '%b %d, %Y'))
                description = unicode(row.find('span', { "class":"middleheadline" }).parent.contents[6])
                bill_list2 = extract_legislation(title)
                for bill in bill_list2:
                    if bill in bill_list:
                        None
                    else:
                        bill_list.append(bill)
                if title == "":
                    title = "".join(bill_list)
                description = ""
                local_file = ""
                file_name = row.find('span', { "class":"middleheadline" }).parent.contents[7]['href']
                original_url = "%s%s" % (base_url, file_name)
                gov_id = "SRP %s-%s" % (congress, release_date)
        
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