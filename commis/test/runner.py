from django.conf import settings
from django.test.simple import build_suite, build_test, reorder_suite, DjangoTestSuiteRunner, TEST_MODULE

class CommisTestSuiteRunner(DjangoTestSuiteRunner):
    def setup_test_environment(self, **kwargs):
        settings.HAYSTACK_SEARCH_ENGINE = 'commis_whoosh'
        settings.HAYSTACK_WHOOSH_STORAGE = 'ram'
        settings.CELERY_ALWAYS_EAGER = True
        settings.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
        super(CommisTestSuiteRunner, self).setup_test_environment(**kwargs)
