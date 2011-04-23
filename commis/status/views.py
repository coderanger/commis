from django.conf.urls.defaults import patterns, url
from django.template.response import TemplateResponse

from commis.generic_views import CommisViewBase
from commis.nodes.models import Node

class StatusView(CommisViewBase):
    app_label = 'status'

    def status(self, request):
        return TemplateResponse(request, 'commis/status/status.html', {
            'nodes': Node.objects.all(),
        })

    def get_urls(self):
        return patterns('',
            url(r'^$',
                self.status,
                name='commis_webui_%s' % self.get_app_label()),
        )
