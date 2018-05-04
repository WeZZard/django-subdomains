try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import patterns, url  # noqa

<<<<<<< HEAD
from ..urls.default import urlpatterns as default_patterns
=======
from ...tests.urls.default import urlpatterns as default_patterns
>>>>>>> django2tmp


urlpatterns = default_patterns
