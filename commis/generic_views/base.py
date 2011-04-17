from django.utils.decorators import classonlymethod

class CommisGenericViewBase(object):
    model = None
    app_label = None
    model_name = None

    def get_app_label(self):
        return self.app_label or self.model._meta.app_label

    def get_model_name(self):
        return self.model_name or self.model._meta.object_name

    def get_urls(self):
        raise NotImplementedError

    @property
    def urls(self):
        return self.get_urls()

    @classonlymethod
    def as_view(cls):
        self = cls()
        return self.urls
