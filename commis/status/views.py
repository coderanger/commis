from commis.generic_views import CommisViewBase

class StatusView(CommisViewBase):
    app_label = 'status'

    def search(self, request):
        pass

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url
        urlpatterns = patterns('',
            url(r'^$',
                self.search,
                name='commis_webui_%s' % self.get_app_label()),
        )
        return urlpatterns
