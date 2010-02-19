from BeautifulSoup import BeautifulSoup
from public_site.congress_utils import extract_legislation, congress_from_year
from django.core.management.base import NoArgsCommand
from docserver.public_site.models import Document, DocumentLegislation
from scrape_utils import archive_file
import datetime, time
import re
import urllib2

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        doc_type = "DPC LB"
        file_type = "html"
        add_date = datetime.datetime.now()
        year = add_date.year
        congress = congress_from_year(year)
        url_prefix = "http://dpc.senate.gov/"
        url = "%sdpcreports.cfm?cf_year=%s" % (url_prefix, year)
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page)
        
        rows = soup.findAll('p', { "class":"doclist" })
        for row in rows:
            file_name = row('a')[0]['href'].strip()
            p = re.compile('dpcdoc\.cfm\?doc_name=')
            standard_format = p.findall(file_name)
            if standard_format:
                gov_id = file_name.replace('dpcdoc.cfm?doc_name=', '').upper()
            else:
                gov_id = None
            original_url = "%s%s" % (url_prefix, file_name)
            local_file = ''
            title = row('a')[0].string
            description = ''
            bill_list = extract_legislation(title)
            date_str = row.contents[3].string.replace('(', '').replace(')', '')
            release_date = time.strftime('%Y-%m-%d', time.strptime(date_str, '%m/%d/%y'))
            
            matches = Document.objects.filter(doc_type=doc_type, gov_id=gov_id, release_date=release_date)
            if len(matches) == 0:
                if gov_id:
                    local_file = archive_file(original_url, gov_id, doc_type, file_type)
                    time.sleep(2)
                    print_page = urllib2.urlopen('file://%s' % local_file).read()
                    soup = BeautifulSoup(print_page)
                    try:
                        full_text = ''.join(soup.findAll('body')[1].findAll(text=True)).strip()
                        full_text = re.sub("\s+" , " ", full_text).replace('&nbsp;', '')
                    except:
                        full_text = ''
                    doc = Document(gov_id=gov_id, release_date=release_date, add_date=add_date, title=title, 
                        description=description, doc_type=doc_type, original_url=original_url, 
                        local_file=local_file, full_text=full_text)
                    doc.save()
                    for bill_num in bill_list:
                        bill_dupe = DocumentLegislation.objects.filter(congress=congress).filter(bill_num=bill_num).filter(document=doc)
                        if not bill_dupe:
                            bill = DocumentLegislation(congress=congress, bill_num=bill_num, document=doc)
                            bill.save()
