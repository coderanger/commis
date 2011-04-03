from fnmatch import fnmatch

from django.conf import settings
from django.db.models import get_app, get_apps
from django.test.simple import build_suite, build_test, reorder_suite, DjangoTestSuiteRunner, TEST_MODULE
from django.test.testcases import TestCase
from django.utils import unittest
from django.utils.importlib import import_module

from commis.utils.modules import guess_app

class CommisTestSuiteRunner(DjangoTestSuiteRunner):
    def setup_test_environment(self, **kwargs):
        settings.HAYSTACK_SEARCH_ENGINE = 'commis_whoosh'
        settings.HAYSTACK_WHOOSH_STORAGE = 'ram'
        settings.CELERY_ALWAYS_EAGER = True
        settings.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
        super(CommisTestSuiteRunner, self).setup_test_environment(**kwargs)

    def build_suite(self, test_labels, extra_tests=None, **kwargs):
        suite = unittest.TestSuite()

        if test_labels:
            for label in test_labels:
                if '.' in label:
                    suite.addTest(build_test(label))
                else:
                    app = get_app(label)
                    suite.addTest(build_suite(app))
        else:
            for app in get_apps():
                app_name = guess_app(app)
                for pattern in getattr(settings, 'TEST_WHITELIST', ('%s.*'%__name__.split('.')[0],)):
                    if fnmatch(app_name, pattern):
                        suite.addTest(build_suite(app))
                        break

            for name in getattr(settings, 'TEST_EXTRA', ()):
                mod = import_module(name + '.' + TEST_MODULE)
                extra_suite = unittest.defaultTestLoader.loadTestsFromModule(mod)
                suite.addTest(extra_suite)


        if extra_tests:
            for test in extra_tests:
                suite.addTest(test)

        return reorder_suite(suite, (TestCase,))
