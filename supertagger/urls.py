from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('',
	# common views
	url(r'^$', 'tagger.views.tagger', name='tagger'),
)

urlpatterns += patterns('',
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.STATIC_ROOT,
    }),
)
