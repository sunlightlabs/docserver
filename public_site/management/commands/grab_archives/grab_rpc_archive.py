from django.core.management.base import NoArgsCommand
import datetime, time
import urllib2
from BeautifulSoup import BeautifulSoup
from docserver.public_site.models import Document

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        doc_type = "GAO"
        page = urllib2.urlopen("http://rpc.senate.gov/public/index.cfm?FuseAction=Documents.Notices&StartDate=01/01/2009&EndDate=03/01/2009")
        soup = BeautifulSoup(page)
        #rows = soup.findAll('td', width="5%", align="center", valign="top")
        rows = soup.findAll('tr')
        print rows[8]