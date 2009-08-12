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
        
        congress = 111
        add_date = datetime.datetime.now()
        doc_type = "RPC LN"
        page = urllib2.urlopen("http://rpc.senate.gov/public/index.cfm?FuseAction=Documents.Notices&StartDate=01/01/2009&EndDate=12/31/2009")
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
            title = a.string.strip().split(' - ', 1)[1].lstrip().encode('ascii', 'ignore')
            title = title.replace("&euro;&trade;", "'").replace("&euro;&rdquo;", "-").replace("&euro;&ldquo;", "-")
            description = ""
            local_file = ""
            bill_list = extract_legislation(title)
            for bill in bill_list:
                if bill in bill_list:
                    None
                else:
                    bill_list.append(bill)
            
            print date_str
            print original_url
            print gov_id
            print title
            
            matches = Document.objects.filter(doc_type=doc_type, gov_id=gov_id, release_date=release_date)
            if len(matches) > 0:
                pass
            else:
                if gov_id != None:
                    try:
                        file_name = "/var/www/data/docserver/rcr_srp/%s.html" % gov_id.replace(' ', '_')
                        remote_file = urllib2.urlopen(original_url)
                        local_file = open(file_name, "w")
                        local_file.write(remote_file.read())
                        local_file.close
                        print gov_id
                    except:
                        print "nope"
                    doc = Document(gov_id=gov_id, release_date=release_date, add_date=add_date, title=title, 
                        description=description, doc_type=doc_type, original_url=original_url, local_file=local_file)
                    doc.save()
        
                    for bill in bill_list:
                        bill_num = bill.replace(' ', '')
                        bill = DocumentLegislation(congress=congress, bill_num=bill_num, document=doc)
                        bill.save()