from django.contrib.sites.models import Site

def current_site(request):
  site = Site.objects.get_current()
  site.path = request.META.get('PATH_INFO')
  site.query_string = request.META.get('QUERY_STRING')
  if site.query_string:
    site.complete_path = "%s?%s&" % (site.path, site.query_string)
  else:
    site.complete_path = "%s?" % site.path
  return site