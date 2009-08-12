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

        def congress_from_year(year):
            if year < 1789:
                return None
            else:
                return int((year-1789)/2) + 1
        
        year = 2009
        #for year in range(2009,1989,-1):
        chamber = 'House'
        congress = congress_from_year(year)
        session = 2 - (year % 2)
        
        for start_row in range(0,1200,100):
            url = "http://clerk.house.gov/evs/%s/ROLL_%s.asp" % (year, str(start_row).zfill(3))
            print url
            page = urllib2.urlopen(url)
            soup = BeautifulSoup(page)
            for row in soup.table.findAll('tr'):
                vote = row.findAll('td')
                if vote:
                    vote_number = vote[0].a.string
                    date_str = "%s %s" % (year, vote[1].font.string)
                    vote_date = time.strftime('%Y-%m-%d', time.strptime(date_str, '%Y %d-%b'))
                    if vote[2].font.a:
                        issue = vote[2].font.a.string.replace(' ', '')
                    else:
                        issue = vote[2].font.string
                    question = vote[3].font.string
                    result = vote[4].font.string
                    title = vote[5].font.string
            
                    existing_vote = Vote.objects.filter(roll=int(vote_number)).filter(date__year=year).filter(chamber=chamber)
                    if not existing_vote:
                        vote_record = Vote(chamber=chamber, congress=congress, session=session,
                            roll=int(vote_number), date=vote_date, issue=issue, question=question, 
                            result=result, title=title)
                        vote_record.save()
            
                        path = '/var/www/data/votes/house/%s-%s/' % (congress, session)
                        url = "http://clerk.house.gov/evs/%s/roll%s.xml" % (year, vote_number.zfill(3))
                        print vote_date
                        os.system("wget -O %sroll_%s_%s_%s.xml %s" % (path, congress, session, vote_number.zfill(3), url))
                        time.sleep(0.5)