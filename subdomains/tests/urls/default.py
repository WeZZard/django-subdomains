try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import patterns, url  # noqa

<<<<<<< HEAD
from ..views import view
=======
from ...tests.views import view
>>>>>>> django2tmp


urlpatterns = patterns('',
    url(regex=r'^$', view=view, name='home'),
    url(regex=r'^example/$', view=view, name='example'),
)
