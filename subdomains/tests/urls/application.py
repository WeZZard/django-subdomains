try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import patterns, url  # noqa

from ..urls.default import urlpatterns as default_patterns
from ..views import view


urlpatterns = default_patterns + patterns('',
    url(regex=r'^view/$', view=view, name='view'),
    url(regex=r'^application/$', view=view, name='application'),
)
