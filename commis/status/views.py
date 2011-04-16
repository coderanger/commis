from commis.generic_views import CommisViewBase
from commis.nodes.models import Node
from django.template.response import TemplateResponse

class StatusView(CommisViewBase):
    app_label = 'status'

    def status(self, request):
        return TemplateResponse(request, 'commis/status/status.html', {
            'nodes': Node.objects.all(),
        })

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url
        urlpatterns = patterns('',
            url(r'^$',
                self.status,
                name='commis_webui_%s' % self.get_app_label()),
        )
        return urlpatterns
