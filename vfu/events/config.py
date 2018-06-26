# coding=utf-8
from vfu.events import MessageFactory as _

def get_vocabs():
	vocabs = {
	    'gender': (
	    		('male', _(u'Male')), 
	    		('female', _(u'Female')),
	    	),
	    'pricing': (
	    		('member', _(u'Member')), 
	    		('regular', _(u'Regular')),
	    		('discount', _(u'Discount')),
	    	),
	    'pricing_roundtable': (
	    		('member', _(u'Member')), 
	    		('discount', _(u'Discount')),
	    		('speaker', _(u'Speaker'))
	    	),
	    'arrival': (
	    		('car', _(u'Car')), 
	    		('train', _(u'Train')), 
	    		('plain', _(u'Plain')), 
	    	), 

	    'title': (
	    		('dr', _(u'Dr')), 
	    		('prof.dr.', _(u'Prof. Dr.')),
	    	)
	}
	return vocabs