from django.urls import path, include
from django.urls import URLPattern
from django.contrib.admin.models import settings

from typing import Tuple
from typing import List
from typing import Any


class SubdomainURLConf(object):
    urlpatterns: List[URLPattern]
    app_name: str
    namespace: str

    def __init__(self: 'SubdomainURLConf', urlconf: str):
        # Sorry but I don't know the type annotation of a Python module.
        # The first element of the tuple is ``Any`` instead.
        urlconf_pack: Tuple[Any, str, str] = include(urlconf)
        self.urlpatterns = [
            path('', urlconf_pack),
            path('', include(settings.ROOT_URLCONF))
        ]
        (_, self.app_name, self.namespace) = urlconf_pack
