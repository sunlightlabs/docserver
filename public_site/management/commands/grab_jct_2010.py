from BeautifulSoup import BeautifulSoup, SoupStrainer
from congress_utils import *
from public_site.models import Document, DocumentLegislation
from django.core.management.base import NoArgsCommand
from scrape_utils import *
import datetime, time
import urllib2

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        doc_type = "JCT"
        file_type = "pdf"
        base_url = "http://jct.gov"
        page = urllib2.urlopen("http://www.jct.gov/publications.html?func=select&id=48")
        add_date = datetime.datetime.now()
        
        soup = BeautifulSoup(page)
        doc_list = soup.findAll(attrs={"class":"jct_fileblock"})
        for doc in doc_list:
            original_url = "%s%s" % (base_url, doc.find('a')['href'])
            doc_page = urllib2.urlopen(original_url)
            doc_soup = BeautifulSoup(doc_page)
            title = doc_soup.find('title')
            gov_id = title.string
            description = doc_soup.find('meta', attrs={'name':'description'})['content']
            remository = doc_soup.findAll('div', attrs={'id':'remositoryfileinfo'})
            for info in remository:
                original_url = "%s%s" % (base_url, info.findAll('a')[0]['href'])
                date_str = info.findAll('dt')[1].nextSibling.nextSibling.contents[0].strip()
                try:
                    release_date = time.strftime('%Y-%m-%d', time.strptime(date_str, '%B %d, %Y'))
                except:
                    release_date = None
                year = time.strptime(date_str, '%B %d, %Y')[0]
                congress = congress_from_year(year)
                title = description.encode('ascii', 'ignore')
                bill_list = extract_legislation(title)
  
                matches = Document.objects.filter(doc_type=doc_type, gov_id=gov_id, release_date=release_date)
                if len(matches) == 0:
                    if gov_id:
                        #local_file = archive_file(original_url, gov_id, doc_type, file_type)
                        local_file = None
                        #full_text = pdf_extract_text(local_file, original_url)
                        full_text = None
                        doc = Document(gov_id=gov_id, release_date=release_date, add_date=add_date, title=title, 
                            description=description, doc_type=doc_type, original_url=original_url, 
                            local_file=local_file, full_text=full_text)
                        doc.save()
                        for bill in bill_list:
                            bill_num = bill.replace(' ', '')
                            bill = DocumentLegislation(congress=congress, bill_num=bill_num, document=doc)
                            bill.save()
