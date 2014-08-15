# -*- coding: utf-8 -*-

from math import floor
import collections
import re

def mostcommon(d):
	return sorted(d.items(), key=lambda x:x[1], reverse=True)[0]

def frequency_dict(multitags):
	term_count={}
	for t in multitags:
		try: term_count[t]+=1
		except KeyError: term_count[t]=1
	return term_count

class Tag:
	def __init__(self, string, stem=None, rating=1.0, proper=False, terminal=False):
		self.string  = string
		self.stem = stem or string
		self.rating = rating
		self.proper = proper
		self.terminal = terminal
        
	def __eq__(self, other):
		return self.stem == other.stem

	def __repr__(self):
		return repr(self.string)

	def __lt__(self, other):
		return self.rating > other.rating

	def __hash__(self):
		return hash(self.stem)


class MultiTag(Tag):
	    
	def __init__(self, tail, head=None):
		if not head:
			Tag.__init__(self, tail.string, tail.stem, tail.rating, tail.proper, tail.terminal)
			self.size = 1
			self.subratings = [self.rating]
		else:
			self.string = ' '.join([head.string, tail.string])
			self.stem = ' '.join([head.stem, tail.stem])
			self.size = head.size + 1

			self.proper = (head.proper and tail.proper)
			self.terminal = tail.terminal

			self.subratings = head.subratings + [tail.rating]
			self.rating = self.combined_rating()
                                           
	def combined_rating(self):
		product = reduce(lambda x, y: x * y, self.subratings, 1.0)
		root = self.size

		if product == 0.0 and self.proper:
			nonzero = [r for r in self.subratings if r > 0.0]
			if len(nonzero) == 0:
				return 0.0
			product = reduce(lambda x, y: x * y, nonzero, 1.0)
			root = len(nonzero)

		return product ** (1.0 / root)

    
class Reader:
	match_apostrophes = re.compile('`|’')
	match_paragraphs = re.compile('[\.\?!\t\n\r\f\v]+')
	match_phrases = re.compile('[,;:\(\)\[\]\{\}<>]+')
	match_words = re.compile('[\w\-\'_/&]+')

	def __call__(self, text):

		text = self.preprocess(text)

		paragraphs = self.match_paragraphs.split(text)

		tags = []

		for par in paragraphs:
			phrases = self.match_phrases.split(par)

			if len(phrases) > 0:
				words = self.match_words.findall(phrases[0])
				if len(words) > 1:
					tags.append(Tag(words[0].lower()))
					for w in words[1:-1]:
						tags.append(Tag(w.lower(), proper=w[0].isupper()))
					tags.append(Tag(words[-1].lower(), proper=words[-1][0].isupper(), terminal=True))
				elif len(words) == 1:
					tags.append(Tag(words[0].lower(), terminal=True))

			for phr in phrases[1:]:
				words = self.match_words.findall(phr)
				if len(words) > 1:
					for w in words[:-1]:
						tags.append(Tag(w.lower(), proper=w[0].isupper()))
				if len(words) > 0:
					tags.append(Tag(words[-1].lower(), proper=words[-1][0].isupper(), terminal=True))

		return tags

	def preprocess(self, text):
		text = self.match_apostrophes.sub('\'', text)
		return text
    
class Stemmer:
	
	match_contractions = re.compile('(\w+)\'(m|re|d|ve|s|ll|t)?')

	def __init__(self, stemmer=None):

		if not stemmer:
			from stemming import porter2
			stemmer = porter2
		self.stemmer = stemmer

	def __call__(self, tag):

		string = self.preprocess(tag.string)
		tag.stem = self.stemmer.stem(string)
		return tag    
        
	def preprocess(self, string):
		match = self.match_contractions.match(string)
		if match: return match.group(1)
		else: return string


class Rater:

	def __init__(self, weights, multitag_size=3):        
		self.weights = weights
		self.multitag_size = multitag_size

	def __call__(self, tags):
		self.rate_tags(tags)
		multitags = self.create_multitags(tags)

		clusters = collections.defaultdict(dict)
		proper = collections.defaultdict(int)
		ratings = collections.defaultdict(float)

		for t in multitags:
			try: clusters[t][t.string] += 1
			except KeyError: clusters[t][t.string] = 1
		if t.proper:
			proper[t] += 1
			ratings[t] = max(ratings[t], t.rating)

		term_count = frequency_dict(multitags)
        
		for t, cnt in term_count.iteritems():
			t.string = mostcommon(clusters[t])[0]
			proper_freq = proper[t] / float(cnt)
			if proper_freq >= 0.5:
				t.proper = True
				t.rating = ratings[t]
        
		unique_tags = set(t for t in term_count
						if len(t.string) > 1 and t.rating > 0.0)

		for t, cnt in term_count.iteritems():
			words = t.stem.split()
			for l in xrange(1, len(words)):
				for i in xrange(len(words) - l + 1):
					s = Tag(' '.join(words[i:i + l]))
					relative_freq = float(cnt) / term_count[s]
					if ((relative_freq == 1.0 and t.proper) or (relative_freq >= 0.5 and t.rating > 0.0)):
						unique_tags.discard(s)
					else:
						unique_tags.discard(t)

		return sorted(unique_tags)

	def rate_tags(self, tags):

		term_count = frequency_dict(tags)
		for t in tags: t.rating = float(term_count[t]) / len(tags) * self.weights.get(t.stem, 1.0)
    
	def create_multitags(self, tags):
   
		multitags = []

		for i in xrange(len(tags)):
			t = MultiTag(tags[i])
			multitags.append(t)
			for j in xrange(1, self.multitag_size):
				if t.terminal or i + j >= len(tags):
					break
				else:
					t = MultiTag(tags[i + j], t)
					multitags.append(t)

		return multitags

    
class Tagger:

	def __init__(self, reader, stemmer, rater):
    
		self.reader = reader
		self.stemmer = stemmer
		self.rater = rater

	def __call__(self, text, tags_number=5):

		tags = self.reader(text)
		tags = map(self.stemmer, tags)
		tags = self.rater(tags)

		return tags[:tags_number]

