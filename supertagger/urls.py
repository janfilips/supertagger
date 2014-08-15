from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('',
	url(r'^$', 'tagger.views.home', name='home'),
	url(r'^supertags/$', 'tagger.views.supertags', name='supertags'),
)

urlpatterns += patterns('',
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.STATIC_ROOT,
    }),
)
