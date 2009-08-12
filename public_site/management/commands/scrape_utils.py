import urllib2
from django.conf import settings

#save file locally 
def archive_file(original_url, gov_id, doc_type, file_type):
    type_dir = doc_type.lower().replace(' ', '_')
    file_name = "%s%s/%s.%s" % (settings.DATA_ROOT, type_dir, gov_id, file_type)
    remote_file = urllib2.urlopen(original_url)
    local_file = open(file_name, "w")
    local_file.write(remote_file.read())
    local_file.close
    return file_name
    

    
def debug_print(output):
    if DEBUG:
        print output