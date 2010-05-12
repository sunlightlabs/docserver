from congress_utils import extract_legislation, clean_bill_num, congress_from_year
from django.core.management.base import NoArgsCommand
from docserver.public_site.models import Document, DocumentLegislation

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        docs = Document.objects.all()
        for doc in docs:
            bill_list = extract_legislation(doc.title)
            congress = congress_from_year(doc.release_date.year)
            if bill_list:
                i = 0
                for bill_num in bill_list:
                    bill_dupe = DocumentLegislation.objects.filter(congress=congress).filter(bill_num=bill_num).filter(document=doc)
                    if not bill_dupe:
                        bill = DocumentLegislation(congress=congress, bill_num=bill_num, document=doc)
                        bill.save()
                        print "%s %s" % (doc.gov_id, bill_list)