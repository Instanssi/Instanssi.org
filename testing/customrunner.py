# -*- coding: utf-8 -*-

from django.test.simple import DjangoTestSuiteRunner
from django.conf import settings


class CustomRunner(DjangoTestSuiteRunner):
    def build_suite(self, *args, **kwargs):
        suite = super(CustomRunner, self).build_suite(*args, **kwargs)
        
        # Get settings
        excluded = getattr(settings, 'TEST_EXCLUDE', [])
        run_all = getattr(settings, 'TEST_RUN_ALL', False)
        
        # Find tests
        if not args[0] and not run_all:
            tests = []
            for case in suite:
                pkg = case.__class__.__module__.split('.')[0]
                if pkg not in excluded:
                    tests.append(case)
            suite._tests = tests 
        return suite
