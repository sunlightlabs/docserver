from django.core.management.base import NoArgsCommand
import feedparser
import datetime, time
from docserver.public_site.models import Document
import urllib2
import os
import pyPdf

class Command(NoArgsCommand):

    def handle_noargs(self,  **options):

        def extract_text(path, original_url):
            print "extracting_text..."
            #adapted from http://code.activestate.com/recipes/511465/
            content = ""
            try:
                pdf = pyPdf.PdfFileReader(file(path, "rb"))
            except:
                print path
                remote_file = urllib2.urlopen(original_url)
                local_file = open(path, "w")
                local_file.write(remote_file.read())
                local_file.close
                time.sleep(2)
                pdf = pyPdf.PdfFileReader(file(path, "rb"))


            for i in range(0, pdf.getNumPages()):
                content += pdf.getPage(i).extractText() + "\n"
            content = " ".join(content.replace("\n", " ").strip().split())
            print "text extracted..."
            return content
        
        doc_type = 'JCT'
        file_type = "pdf"
        path_prefix = '/var/www/data/docserver/'
        path = "%s/" % doc_type.lower().replace(' ', '_')
        full_path = "%s%s" % (path_prefix, path)

        docs = Document.objects.filter(doc_type=doc_type).filter(full_text="")
        for doc in docs:
            file_name = "%s.%s" % (doc.gov_id, file_type)
            print "trying %s" % file_name
            try:
                doc.full_text = extract_text("%s%s" % (full_path, file_name), doc.original_url)
                doc.save()
                print doc.gov_id
            except:
                print "error on %s" % doc.gov_id