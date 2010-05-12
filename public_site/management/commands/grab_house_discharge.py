from django.core.management.base import NoArgsCommand
import datetime, time
import urllib2
from BeautifulSoup import BeautifulSoup
from docserver.public_site.models import Vote
import re
import os
import time

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        
        congress = 111
        
        for discharge_id in range(2,31,1):
            url = "http://clerk.house.gov/%s/lrc/pd/petitions/Dis%s.htm" % (congress, discharge_id)
            print url
            page = urllib2.urlopen(url)
            soup = BeautifulSoup(page)
            hey = soup.findAll('table')[3].findAll('tr')[1]
            print hey
            break
            time.sleep(0.5)