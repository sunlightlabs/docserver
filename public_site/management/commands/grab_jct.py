from django.core.management.base import NoArgsCommand
import datetime, time
import os
import urllib2
from BeautifulSoup import BeautifulSoup, SoupStrainer
from docserver.public_site.models import Document, DocumentLegislation
import re

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        
        # return list of bill numbers extracted from string
        def extract_legislation(haystack):
            if haystack:
                haystack = haystack.upper()
                p = re.compile('S\.\s?CON\.\s?RES\.\s?\d{1,5}|H\.\s?CON\s?RES\.\s?\d{1,5}|S\.\s?J\.\s?RES\.\s\d{1,5}|H\.\s?J\.\s?RES\.\s\d{1,5}|S\.\s?RES\.\s?\d{1,5}|H\.\s?RES\.\s?\d{1,5}|H\.\s?\R\.\s?\d{1,5}|S\.\s?\d{1,5}')
                needle_list = p.findall(haystack)
                return needle_list
            else:
                return []
            
        #returns number of Congress in session for provided year
        def congress_from_year(year):
            if year < 1789:
                return None
            else:
                return int((year-1789)/2) + 1
        
        add_date = datetime.datetime.now()
        doc_type = "JCT"
        base_url = "http://jct.gov"
        page = urllib2.urlopen("http://www.jct.gov/publications.html?func=select&id=17")
        
        soup = BeautifulSoup(page)
        doc_list = soup.findAll(attrs={"class":"jct_fileblock"})
        for doc in doc_list:
            original_url = "%s%s" % (base_url, doc.find('a')['href'])
            doc_page = urllib2.urlopen(original_url)
            doc_soup = BeautifulSoup(doc_page)
            title = doc_soup.find('title')
            gov_id = title.string
            description = doc_soup.find('meta', attrs={'name':'description'})['content']
            print description
            remository = doc_soup.findAll('div', attrs={'id':'remositoryfileinfo'})
            for info in remository:
                original_url = "%s%s" % (base_url, info.findAll('a')[0]['href'])

                date_str = info.findAll('dt')[1].nextSibling.nextSibling.contents[0].strip()
                print date_str
                try:
                    release_date = time.strftime('%Y-%m-%d', time.strptime(date_str, '%B %d, %Y'))
                except:
                    release_date = None
                print release_date
                year = time.strptime(date_str, '%B %d, %Y')[0]
                congress = congress_from_year(year)
                title = description
                bill_list = extract_legislation(title)
                description = ""
                local_file = ""
                print title
  
                matches = Document.objects.filter(doc_type=doc_type, gov_id=gov_id, release_date=release_date)
                if len(matches) > 0:
                    pass
                else:
                    if gov_id != None:
                        try:
                            file_name = "/var/www/data/docserver/jct/%s.pdf" % gov_id
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