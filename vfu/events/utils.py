from AccessControl import Unauthorized
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl.SpecialUsers import system as system_user


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