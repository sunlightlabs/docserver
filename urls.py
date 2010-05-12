from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^docserver/', include('docserver.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/(.*)', admin.site.root),
    (r'^$', 'docserver.public_site.views.index'),
    (r'^iphone/$', 'docserver.public_site.views.iphone'),
    (r'^search/$', 'docserver.public_site.views.search'),
    (r'^timeline/(?P<congress>\d+)-(?P<bill_type>\w+)-(?P<bill_id>\d+)/$', 'docserver.public_site.views.timeline'),
    (r'^bill/(?P<congress>\d+)-(?P<bill_type>\w+)-(?P<bill_id>\d+)/$', 'docserver.public_site.views.bill'),
    (r'^bill/(?P<congress>\d+)-(?P<bill_type>\w+)-(?P<bill_id>\d+)/list.(?P<format>\w+)$', 'docserver.public_site.views.bill'),
    (r'^(?P<doc_type>\w+)/$', 'docserver.public_site.views.typelist'),
    (r'^(?P<doc_type>\w+)/list.(?P<format>\w+)$', 'docserver.public_site.views.typelist'),
)
