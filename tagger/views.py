# -*- coding: utf-8 -*-

import os
import time
import pickle
import logging
import datetime

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext

from django.http import HttpResponseForbidden
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render

logger = logging.getLogger(__name__)

from stemmer import Tagger, Reader, Stemmer, Rater

weights = pickle.load(open('data/dict.pkl', 'rb'))
tagger = Tagger(Reader(), Stemmer(), Rater(weights))

def supertags(request):

	print 'supertags'
	print request.POST
	
	data = request.POST['data']
		
	import time; x = time.time()
	supertags = tagger(data)
	seconds = time.time()-x
		
	output = "Tags: "
	
	for tag in supertags:		
		output += '<b>' + tag.string.upper() + '</b> '
	
	output += '<br/>'
	output += 'Roundtrip time: <b>' + str(seconds) + 's</b><br/><br/>'

	return HttpResponse(output)


def home(request):

	print 'home'
	return render_to_response('tagger.html', {}, context_instance=RequestContext(request))
