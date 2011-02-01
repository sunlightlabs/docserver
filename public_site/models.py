from django.db import models
from django.db import connection
from congress_utils import GT_MAP, clean_bill_num
import djangosphinx
import re
    
class LegislationManager(models.Manager):
    def top_recent(self, days_back, max_rows):
        cursor = connection.cursor()
        sql = """SELECT bill_num, congress, COUNT(bill_num) AS bill_count 
                    FROM public_site_documentlegislation, public_site_document 
                    WHERE public_site_documentlegislation.document_id = public_site_document.id  
                        AND public_site_document.release_date > DATE_SUB(now(), INTERVAL %s DAY) 
                    GROUP BY bill_num 
                    ORDER BY bill_count DESC 
                    LIMIT %s"""
        cursor.execute(sql, (days_back, max_rows))
        return cursor  
    
class Document(models.Model):
    gov_id = models.CharField(max_length=32)
    release_date = models.DateTimeField()
    add_date = models.DateTimeField()
    title = models.TextField()
    description = models.TextField()
    doc_type = models.CharField(max_length=32)
    original_url = models.CharField(max_length=255)
    local_file = models.CharField(max_length=255, null=True)
    full_text = models.TextField(null=True)
    search = djangosphinx.SphinxSearch(
        index='docserver', 
        weights = {
            'title':100,
            'description':20,
            'full_text':10,
        }
    )
    
class DocumentLegislation(models.Model):
    congress = models.IntegerField()
    bill_num = models.CharField(max_length=255)
    document = models.ForeignKey(Document)
    objects = LegislationManager()

    def structured_bill(self):
        if not getattr(self, '_sb', None):
            p = re.compile('([a-z]{1,7})(\d{1,4})')
            m = p.match(self.bill_num.replace('.', '').lower())
            bill_type = m.group(1)
            num = m.group(2)
            clean = clean_bill_num(self.bill_num)
            self._sb = {'congress':self.congress, 'bill_type':bill_type, 'num':num, 'clean':clean}
        return self._sb
    
class Vote(models.Model):
    chamber = models.CharField(max_length=32)
    congress = models.IntegerField()
    session = models.IntegerField()
    roll = models.IntegerField()
    date = models.DateTimeField()
    issue = models.CharField(max_length=255, null=True)
    question = models.TextField()
    result = models.CharField(max_length=32)
    title = models.TextField(null=True)
    
class Action(models.Model):
    date = models.DateTimeField()
    congress = models.IntegerField()
    bill_num = models.CharField(max_length=255)
    description = models.TextField(null=True)
    reference_id = models.CharField(max_length=255, null=True)
    reference_text = models.TextField(null=True)
    
class DocType(models.Model):
    title = models.TextField()
    description = models.TextField()
