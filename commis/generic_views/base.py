from django.conf.urls.defaults import patterns, url
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator, classonlymethod


class CommisGenericViewBase(object):
    model = None
    app_label = None

    def get_app_label(self):
        return self.app_label or self.model._meta.app_label

    def get_urls(self):
        raise NotImplementedError

    @property
    def urls(self):
        return self.get_urls()

    @classonlymethod
    def as_view(cls):
        self = cls()
        return self.urls
