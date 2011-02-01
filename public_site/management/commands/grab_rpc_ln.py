from BeautifulSoup import BeautifulSoup, SoupStrainer
from congress_utils import *
from public_site.models import Document, DocumentLegislation
from django.core.management.base import NoArgsCommand
from scrape_utils import *
import datetime, time
import urllib2

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        doc_type = "RPC LN"
        file_type = "pdf"
        add_date = datetime.datetime.now()
        this_year = add_date.year
        start_str = "01/01/%s" % this_year
        end_str = "12/31/%s" % this_year
        page = urllib2.urlopen("http://rpc.senate.gov/public/index.cfm?FuseAction=Documents.Notices&StartDate=%s&EndDate=%s" % (start_str, end_str))
        
        soup = BeautifulSoup(page)
        legislation_list = soup.findAll(name='td', attrs={'class':'vblack8'})
        for item in legislation_list:
            a = item.find('a')
            original_url = a['href']
            p = re.compile('L\d*')
            gov_id_list = p.findall(original_url)
            if len(gov_id_list) > 0:
                gov_id = gov_id_list[0]
            else:
                gov_id = None
            date_str = a.string.strip().split('-')[0].rstrip()
            release_date = time.strftime('%Y-%m-%d', time.strptime(date_str, '%m/%d/%Y'))
            release_year = int(time.strftime('%Y', time.strptime(date_str, '%m/%d/%Y')))
            congress = congress_from_year(release_year)
            title = a.string.strip().split(' - ', 1)[1].lstrip().encode('ascii', 'ignore')
            title = title.replace("&euro;&trade;", "'").replace("&euro;&rdquo;", "-").replace("&euro;&ldquo;", "-")
            description = ""
            bill_list = extract_legislation(title)
            
            matches = Document.objects.filter(doc_type=doc_type, gov_id=gov_id, release_date=release_date)
            if len(matches) == 0:
                if gov_id:
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