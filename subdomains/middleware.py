import operator
import logging

from django.conf import settings
from django.utils.cache import patch_vary_headers
from django.urls import include
from .SubdomainURLConf import SubdomainURLConf

from .utils import get_domain, get_subdomain

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    # Pre Django 1.10 middleware does not require the mixin.
    MiddlewareMixin = object


logger = logging.getLogger(__name__)
lower = operator.methodcaller('lower')

UNSET = object()


class SubdomainMiddleware(MiddlewareMixin):
    """ Adds a ``subdomain`` attribute to the current request."""

    @staticmethod
    def get_domain_for_request(request):
        """
        Returns the domain that will be used to identify the subdomain part
        for this request.
        """
        return get_domain()

    def __call__(self, request):
        """
        Adds a ``subdomain`` attribute to the ``request`` parameter.
        """

        domain, host = map(
            lower,
            (self.get_domain_for_request(request), request.get_host())
        )

        subdomain, has_found_subdomain = get_subdomain(domain, host)

        request.subdomain = subdomain

        if not has_found_subdomain:
            logger.warning(
                'The host %s does not belong to the domain %s, \
unable to identify the subdomain for this request',
                request.get_host(),
                domain
            )

    def process_response(self, request, response):
        pass


class SubdomainURLRoutingMiddleware(SubdomainMiddleware):
    """ Allows for subdomain-based URL routing. """

    def process_request(self, request):
        """
        Sets the current request's ``urlconf`` attribute to the urlconf
        associated with the subdomain, if it is listed in
        ``settings.SUBDOMAIN_URLCONFS``.
        """
        super(SubdomainURLRoutingMiddleware, self).__call__(request)

        subdomain = getattr(request, 'subdomain', UNSET)

        if subdomain is not UNSET:
            urlconf = settings.SUBDOMAIN_URLCONFS.get(subdomain)
            if urlconf is not None:
                logger.debug(
                    "Using urlconf %s for subdomain: %s",
                    repr(urlconf),
                    repr(subdomain)
                )
                (_, app_name, _) = include(urlconf)
                request.urlconf = SubdomainURLConf(urlconf)

        response = self.get_response(request)

        if getattr(settings, 'FORCE_VARY_ON_HOST', True):
            patch_vary_headers(response, ('Host',))

        return response

    '''def process_response(self, request, response):
        """
        Forces the HTTP ``Vary`` header onto requests to avoid having responses
        cached across subdomains.
        """
        if getattr(settings, 'FORCE_VARY_ON_HOST', True):
            patch_vary_headers(response, ('Host',))

        return response'''
