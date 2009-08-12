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
                
        doc_type = "GAO"
        page = urllib2.urlopen("http://gao.gov/docsearch/pastyear.html")
        soup = BeautifulSoup(page)
        for report in soup('dl'):
            title = report('dt')[0].renderContents().replace('<strong>', '').replace('</strong>', '')
            category = report('dt')[0]('strong')[0].renderContents()
            original_url = report('dd')[0].find('a')['href']
            summary_url = report('dd')[1].find('a')['href']
            summary_page = urllib2.urlopen(summary_url)
            summary_soup = BeautifulSoup(summary_page)
            description = summary_soup('div', {'class':'module_div'})[0].contents[2].contents[0]
            bill_list = extract_legislation(description)
            time.sleep(1.0)
            
            local_file = ''
            gov_id = report('dd')[0].find('a').string.strip()
            date_str = report('dd')[0].find('a').nextSibling.lstrip(', ')
            release_date = time.strftime('%Y-%m-%d', time.strptime(date_str, '%B %d, %Y'))
            release_year = time.strptime(date_str, '%B %d, %Y')[0]
            congress = congress_from_year(release_year)
            add_date = datetime.datetime.now()
            
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
            
            print gov_id