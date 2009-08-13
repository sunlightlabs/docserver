from BeautifulSoup import BeautifulSoup, SoupStrainer
from congress_utils import *
from docserver.public_site.models import Document, DocumentLegislation
from django.core.management.base import NoArgsCommand
from scrape_utils import *
import datetime, time
import urllib2

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        doc_type = "RCR SRP"
        file_type = "html"
        base_url = 'http://repcloakroom.house.gov/news/'
        page = urllib2.urlopen("http://repcloakroom.house.gov/news/DocumentQuery.aspx?DocumentTypeID=1501&Page=2")
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
                if title == "":
                    title = "".join(bill_list)
                file_name = row.find('span', { "class":"middleheadline" }).parent.contents[7]['href']
                original_url = "%s%s" % (base_url, file_name)
                gov_id = "SRP-%s-%s-%s" % (congress, bill_list[0], release_date)
        
                matches = Document.objects.filter(doc_type=doc_type, gov_id=gov_id, release_date=release_date)
                if len(matches) == 0:
                    if gov_id:
                        local_file = archive_file(original_url, gov_id, doc_type, file_type)
                        doc = Document(gov_id=gov_id, release_date=release_date, add_date=add_date, title=title, description=description, doc_type=doc_type, original_url=original_url, local_file=local_file)
                        doc.save()
                        for bill in bill_list:
                            bill_num = bill.replace(' ', '')
                            bill = DocumentLegislation(congress=congress, bill_num=bill_num, document=doc)
                            bill.save()