from .base import *

from django_auth_ldap.config import LDAPSearch, GroupOfNamesType

import ldap

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_LDAP_SERVER_URI = "ldap://monnow.tiger-computing.wbp"

AUTH_LDAP_BIND_DN = ""

AUTH_LDAP_BIND_PASSWORD = ""

AUTH_LDAP_USER_SEARCH = LDAPSearch(
    "dc=tiger-computing,dc=co,dc=uk", ldap.SCOPE_SUBTREE, "(uid=%(user)s)"
)

AUTH_LDAP_START_TLS = True

AUTH_LDAP_GLOBAL_OPTIONS = {ldap.OPT_X_TLS_REQUIRE_CERT: ldap.OPT_X_TLS_NEVER}

AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName", "last_name": "sn", "email": "mail"
}

AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_staff": "cn=tcl-piesup,ou=groups,dc=tiger-computing,dc=co,dc=uk",
    "is_superuser": "cn=tcl-piesup,ou=groups,dc=tiger-computing,dc=co,dc=uk"
}

AUTH_LDAP_GROUP_TYPE = GroupOfNamesType()

AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    "ou=groups,dc=tiger-computing,dc=co,dc=uk",
    ldap.SCOPE_SUBTREE,
    "(objectClass=groupOfNames)"
)

AUTH_LDAP_MIRROR_GROUPS = True
