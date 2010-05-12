from django.core.management.base import NoArgsCommand
import datetime, time
import urllib2
from BeautifulSoup import BeautifulStoneSoup
from docserver.public_site.models import Action
import re
import os
import time

class Command(NoArgsCommand):

    def handle_noargs(self, **options):

        congress = 109
        path = "/var/www/data/govtrack/%s/bills/" % congress
        
        dirList=os.listdir(path)
        for fname in dirList:        
            url = "%s%s" % (path,fname)
            page = urllib2.urlopen("file:%s" % url)
            soup = BeautifulStoneSoup(page)
            bill_num = "%s%s" % (soup.bill['type'], soup.bill['number'])
            
            if soup.bill.actions:
                for action in soup.bill.actions.findAll('action'):
                    date = datetime.datetime.fromtimestamp(float(action['date']))
                    date += datetime.timedelta(hours=1)
                    committee = None
                    if action.committee:
                        committee = action.committee
                    description = action.text.string
                    reference_id = None
                    reference_text = None
                    if action.reference:
                        reference_id = action.reference['label']
                        reference_text = action.reference['ref']
                    
                    existing_action = Action.objects.filter(date=date, congress=congress, 
                        bill_num=bill_num, description=description, 
                        reference_id=reference_id, reference_text=reference_text)
                
                    if not existing_action:
                        action_record = Action(date=date, congress=congress, 
                            bill_num=bill_num, description=description, 
                            reference_id=reference_id, reference_text=reference_text)
                        print reference_id
                        action_record.save()
                        print "saved"