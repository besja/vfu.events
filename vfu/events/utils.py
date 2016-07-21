import re

from AccessControl import Unauthorized
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl.SpecialUsers import system as system_user

from zope.interface import invariant, Invalid

from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from vfu.events.config import get_vocabs 
from datetime import timedelta, date

from vfu.events import MessageFactory as _

def trusted(fn):
    """
    Executes the callable as a Zope superuser if original call raises
    Unauthorized.
    """
    def trusted_fn(*args, **kwargs):
        try:
            value = fn(*args, **kwargs)
        except Unauthorized:
            orig_sec_mgr = getSecurityManager()
            newSecurityManager(None, system_user)
            value = fn(*args, **kwargs)
            setSecurityManager(orig_sec_mgr)
        return value
    return trusted_fn


# RFC 2822 local-part: dot-atom or quoted-string
# characters allowed in atom: A-Za-z0-9!#$%&'*+-/=?^_`{|}~
# RFC 2821 domain: max 255 characters
_LOCAL_RE = re.compile(r'([A-Za-z0-9!#$%&\'*+\-/=?^_`{|}~]+'
                     r'(\.[A-Za-z0-9!#$%&\'*+\-/=?^_`{|}~]+)*|'
                     r'"[^(\|")]*")@[^@]{3,255}$')

# RFC 2821 local-part: max 64 characters
# RFC 2821 domain: sequence of dot-separated labels
# characters allowed in label: A-Za-z0-9-, first is a letter
# Even though the RFC does not allow it all-numeric domains do exist
_DOMAIN_RE = re.compile(r'[^@]{1,64}@[A-Za-z0-9][A-Za-z0-9-]*'
                                r'(\.[A-Za-z0-9][A-Za-z0-9-]*)+$')

def validateaddress(value):

    if not _LOCAL_RE.match(value):
        raise Invalid(_(u'Invalid email address.'))
    if not _DOMAIN_RE.match(value):
        raise Invalid(_(u'Invalid email address.'))
    return True

def list_to_voc(name):
    vocs = get_vocabs();
    voc = vocs[name]
    terms = []
    for i in voc:
        terms.append(SimpleTerm(value=i[0], title=i[1]))
    return SimpleVocabulary(terms)

def genderConstraint(value):
    if not value:
        raise Invalid(_(u"Select your gender"))
    return True


def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)