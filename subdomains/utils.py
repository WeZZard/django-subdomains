import functools
from typing import Optional
import re
try:
    from urlparse import urlsplit, urlunparse, urlunsplit
except ImportError:
    from urllib.parse import urlsplit, urlunparse, urlunsplit

from django.conf import settings
<<<<<<< HEAD
try:
    from django.core.urlresolvers import reverse as simple_reverse
except ImportError:  # Django 2.0
    from django.urls import reverse as simple_reverse
=======
from django.urls import resolve as _primitive_resolve
from django.urls import reverse as _primitive_reverse
from django.urls import NoReverseMatch, get_resolver
from django.utils import lru_cache
>>>>>>> django2tmp


def get_domain() -> str:
    if hasattr(settings, 'SUBDOMAINS_DOMAIN') and settings.SUBDOMAINS_DOMAIN:
        return settings.SUBDOMAINS_DOMAIN
    else:
        from django.contrib.sites.models import Site
        domain = Site.objects.get_current().domain

        prefix = 'www.'
        if getattr(settings, 'REMOVE_WWW_FROM_DOMAIN', False) \
                and domain.startswith(prefix):
            domain = domain.replace(prefix, '', 1)

        return domain


def get_subdomain(domain: str, host: str) -> (Optional[str], bool):
    """
    Find the subdomain of host if host is a subdomain of parent_domain.

    :param domain: the domain, e.g. ``example.com``
    :param host: the hostname, e.g. ``www.example.com``
    :returns: the subdomain (e.g. ``www``) and a boolean indicating if it was
    found
    """
    pattern = r'^(?:(?P<subdomain>.*?)\.)?%s(?::.*)?$' % re.escape(domain)
    matches = re.match(pattern, host)
    if matches:
        return matches.group('subdomain'), True
    return None, False


def urljoin(domain: str, path: str=None, scheme: str=None) -> str:
    """
    Joins a domain, path and scheme part together, returning a full URL.

    :param domain: the domain, e.g. ``example.com``
    :param path: the path part of the URL, e.g. ``/example/``
    :param scheme: the scheme part of the URL, e.g. ``http``, defaulting to the
        value of ``settings.DEFAULT_URL_SCHEME``
    :returns: a full URL
    """
    if scheme is None:
        scheme = getattr(settings, 'DEFAULT_URL_SCHEME', 'http')

    return urlunparse((scheme, domain, path or '', None, None, None))


def reverse(
        view_name: str,
        subdomain: str=None,
        scheme: str=None,
        args=None,
        kwargs=None,
        current_app: str=None,
        path_only: str=False
) -> str:
    """
    Reverses a URL from the given parameters, in a similar fashion to
    :meth:`django.urls.reverse`.

    :param view_name: the name of URL
    :param subdomain: the subdomain to use for URL reversing
    :param scheme: the scheme to use when generating the full URL
    :param args: positional arguments used for URL reversing
    :param kwargs: named arguments used for URL reversing
    :param current_app: hint for the currently executing application
    :param path_only: return the path only instead of an absolute URL
    """
    return _reverse(
        view_name,
        subdomain=subdomain,
        scheme=scheme,
        args=args,
        kwargs=kwargs,
        current_app=current_app,
        path_only=path_only
    )


def _reverse(
        view_name: str,
        subdomain: str=None,
        scheme: str=None,
        args=None,
        kwargs=None,
        current_app: str=None,
        path_only: bool=False,
        allows_fallback: bool=True
) -> str:
    """Actually reverse a URL from the given parameters."""
    urlconf = settings.SUBDOMAIN_URLCONFS.get(subdomain, settings.ROOT_URLCONF)

    domain = get_domain()
    if subdomain is not None and not (
            getattr(settings, "SUBDOMAINS_AVOID_IF_ROOT_URLCONF", False) and
            urlconf == settings.ROOT_URLCONF
    ):
        domain = '%s.%s' % (subdomain, domain)

    try:
        path = _primitive_reverse(
            view_name,
            urlconf=urlconf,
            args=args,
            kwargs=kwargs,
            current_app=current_app
        )
        if path_only:
            return path
        return urljoin(domain, path, scheme=scheme)

    except NoReverseMatch as exc:
        # If nothing was found and SUBDOMAINS_AUTO_NAMESPACE_FALLBACK is set,
        # try to find a subdomain that matches the view namespace, and use that
        # to run the search again.
        if allows_fallback \
           and getattr(settings, "SUBDOMAINS_AUTO_NAMESPACE_FALLBACK", False) \
           and isinstance(view_name, str) and ':' in view_name:
            ns = view_name.split(':')[0]
            has_found, fallback_subdomain = find_subdomain_by_namespace(ns)
            if has_found:
                return _reverse(
                    view_name,
                    subdomain=fallback_subdomain,
                    scheme=scheme,
                    args=args,
                    kwargs=kwargs,
                    current_app=current_app,
                    path_only=path_only,
                    allows_fallback=False
                )

        # Not found :/
        raise exc


@lru_cache.lru_cache(maxsize=None)
def find_subdomain_by_namespace(namespace: str) -> (bool, bool):
    for subdomain, urlconf in settings.SUBDOMAIN_URLCONFS.items():
        resolver = get_resolver(urlconf)
        if namespace == resolver.namespace \
           or namespace in resolver.namespace_dict:
            return True, subdomain
    return False, None


#: :func:`reverse` bound to insecure (non-HTTPS) URLs scheme
insecure_reverse = functools.partial(reverse, scheme='http')

#: :func:`reverse` bound to secure (HTTPS) URLs scheme
secure_reverse = functools.partial(reverse, scheme='https')

#: :func:`reverse` bound to be relative to the current scheme
relative_reverse = functools.partial(reverse, scheme='')


def resolve(path: str, urlconf=None) -> str:
    url = urlsplit(path)
    if url.netloc != "":
        # Absolute URL: guess the urlconf
        domain, host = get_domain(), url.hostname
        subdomain, has_found = get_subdomain(domain, host)
        if has_found:
            urlconf = settings.SUBDOMAIN_URLCONFS.get(
                subdomain,
                settings.ROOT_URLCONF
            )

        # Now build the path
        path = urlunsplit(("", "", url[2], url[3], url[4]))

    # Use Django's resolve with what's left
    return _primitive_resolve(path, urlconf=urlconf)
