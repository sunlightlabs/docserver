from django.core.management.base import NoArgsCommand
import datetime, time
import urllib2
from BeautifulSoup import BeautifulStoneSoup
from docserver.public_site.models import Vote
import re
import os
import time

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        
        def strip_tags(value):
            return re.sub(r'<[^>]*?>', '', value) 
        
        def congress_from_year(year):
            if year < 1789:
                return None
            else:
                return int((year-1789)/2) + 1
        
        chamber = "Senate"
        year = 2009
        #for year in range(2009,1988,-1):
        congress = congress_from_year(year)
        session = 2 - (year % 2)

        path = '/var/www/data/votes/senate/%s-%s/' % (congress, session)
        url = "http://www.senate.gov/legislative/LIS/roll_call_lists/vote_menu_%s_%s.xml" % (congress, session)
        page = urllib2.urlopen(url)
        os.system("wget -O %svote_menu_%s_%s.xml %s" % (path, congress, session, url))
        soup = BeautifulStoneSoup(page)
        for vote in soup.vote_summary.votes.findAll('vote'):
            vote_number = vote.vote_number.string
            date_str = "%s %s" % (year, vote.vote_date.string)
            vote_date = time.strftime('%Y-%m-%d', time.strptime(date_str, '%Y %d-%b'))
            if vote.issue.find('a'):
                issue = vote.issue.find('a').string.replace(' ', '').replace('.', '')
            else:
                issue = vote.issue.string
            question = strip_tags(str(vote.question))
            result = vote.result.string
            title = vote.title.string

            existing_vote = Vote.objects.filter(chamber=chamber).filter(roll=int(vote_number)).filter(date__year=year)
            if not existing_vote:
                vote_record = Vote(chamber=chamber, congress=congress, session=session,
                    roll=int(vote_number), date=vote_date, issue=issue, question=question, 
                    result=result, title=title)
                vote_record.save()          