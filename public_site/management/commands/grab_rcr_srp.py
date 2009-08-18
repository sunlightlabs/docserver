from BeautifulSoup import BeautifulSoup, SoupStrainer
from congress_utils import *
from docserver.public_site.models import Document, DocumentLegislation
from django.core.management.base import NoArgsCommand
from scrape_utils import *
import datetime, time
import re
import urllib2

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        doc_type = "RCR SRP"
        file_type = "html"
        base_url = 'http://repcloakroom.house.gov/news/'
        page = urllib2.urlopen("http://repcloakroom.house.gov/news/DocumentQuery.aspx?DocumentTypeID=1501&Page=1")
        add_date = datetime.datetime.now()
        
        soup = BeautifulSoup(page)
        rows = soup.findAll('span', { "class":"middlecopy" })
        for row in rows:
            if row.find('span', { "class":"middleheadline" }):
                title = str(row.find('span', { "class":"middleheadline" }).contents[1]).replace('<b>', '').replace('</b>', '').strip()
                bill_list = extract_legislation(title)
                date_str = row.find('span', { "class":"middleheadline" }).parent.contents[5].contents[0].replace('&nbsp;-', '').strip()
                release_date = time.strftime('%Y-%m-%d', time.strptime(date_str, '%b %d, %Y'))
                year = int(time.strftime('%Y', time.strptime(date_str, '%b %d, %Y')))
                congress = congress_from_year(year)
                description = unicode(row.find('span', { "class":"middleheadline" }).parent.contents[6]).strip()
                if not bill_list:
                    bill_list = extract_legislation(description)
                if title == "":
                    title = "".join(bill_list)
                file_name = row.find('span', { "class":"middleheadline" }).parent.contents[7]['href']
                original_url = "%s%s" % (base_url, file_name)
                gov_id = "SRP-%s-%s-%s" % (congress, bill_list[0].replace(' ', '').replace('.', ''), release_date)
                matches = Document.objects.filter(doc_type=doc_type, gov_id=gov_id, release_date=release_date)

                if len(matches) == 0:
                    print_url = original_url.replace('DocumentSingle', 'DocumentPrint')
                    print_page = urllib2.urlopen(print_url).read()
                    full_text = ''.join(BeautifulSoup(print_page).findAll(text=True)).replace('DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"', '').strip()
                    full_text = re.sub("\s+" , " ", full_text)
                    if gov_id:
                        local_file = archive_file(original_url, gov_id, doc_type, file_type)
                        doc = Document(gov_id=gov_id, release_date=release_date, add_date=add_date, title=title, description=description, doc_type=doc_type, original_url=original_url, local_file=local_file, full_text=full_text)
                        doc.save()
                        for bill in bill_list:
                            bill_num = bill.replace(' ', '')
                            bill = DocumentLegislation(congress=congress, bill_num=bill_num, document=doc)
                            bill.save()