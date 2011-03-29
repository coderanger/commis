# From https://github.com/mixcloud/django-celery-haystack-SearchIndex/blob/master/queued_indexer.py
from django.db.models import signals
from django.db.models.loading import get_model
from haystack import indexes
from haystack import site

from commis.search.tasks import SearchIndexUpdateTask
from commis.utils.dict import flatten_dict

def remove_instance_from_index(instance):
    model_class = get_model(instance._meta.app_label, instance._meta.module_name)
    search_index = site.get_index(model_class)
    search_index.remove_object(instance)


class QueuedSearchIndex(indexes.SearchIndex):
    """
    A ``SearchIndex`` subclass that enqueues updates for later processing.

    Deletes are handled instantly since a reference, not the instance, is put on the queue. It would not be hard
    to update this to handle deletes as well (with a delete task).
    """
    # We override the built-in _setup_* methods to connect the enqueuing operation.
    def _setup_save(self, model):
        signals.post_save.connect(self.enqueue_save, sender=model)

    def _setup_delete(self, model):
        signals.post_delete.connect(self.enqueue_delete, sender=model)

    def _teardown_save(self, model):
        signals.post_save.disconnect(self.enqueue_save, sender=model)

    def _teardown_delete(self, model):
        signals.post_delete.disconnect(self.enqueue_delete, sender=model)

    def enqueue_save(self, instance, **kwargs):
        SearchIndexUpdateTask.apply_async(args=[instance._meta.app_label, instance._meta.module_name, instance._get_pk_val()])

    def enqueue_delete(self, instance, **kwargs):
        remove_instance_from_index(instance)


class CommisSearchIndex(QueuedSearchIndex):
    text = indexes.CharField(document=True)
    id_order = indexes.CharField()

    def prepare_text(self, obj):
        buf = []
        for key, values in flatten_dict(obj.to_search()).iteritems():
            for value in values:
                buf.append('%s__=__%s'%(key, value))
        return '\n'.join(buf)

    def prepare_id_order(self, obj):
        return '%016d'%obj.id
