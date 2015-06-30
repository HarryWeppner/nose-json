"""
nose_json.plugin
~~~~~~~~~~~~~~~~

:copyright: 2012 DISQUS.
:license: BSD
"""
import codecs
import os
import simplejson
import traceback
from time import time
from ts_time import rdtsc
from nose.exc import SkipTest
from nose.plugins import Plugin
from nose.plugins.xunit import id_split, nice_classname, exc_message


class JsonReportPlugin(Plugin):
    name = 'json'
    score = 2000
    encoding = 'UTF-8'

    def _get_time_taken(self):
        if hasattr(self, '_timer'):
            taken = time() - self._timer
        else:
            # test died before it ran (probably error in setup())
            # or success/failure added before test started probably
            # due to custom TestResult munging
            taken = 0.0
        return taken

    def _get_tsc_timestamp(self):
        """Returns a tuple of time and tsc timestamp"""

        return (time(), rdtsc())

    def options(self, parser, env):
        Plugin.options(self, parser, env)
        parser.add_option(
            '--json-file', action='store',
            dest='json_file', metavar="FILE",
            default=env.get('NOSE_JSON_FILE', 'nosetests.json'),
            help=("Path to json file to store the report in. "
                  "Default is nosetests.json in the working directory "
                  "[NOSE_JSON_FILE]"))

    def configure(self, options, config):
        Plugin.configure(self, options, config)
        self.config = config
        if not self.enabled:
            return

        self.stats = {
            'errors': 0,
            'failures': 0,
            'passes': 0,
            'skipped': 0,
        }
        self.results = []

        report_output = options.json_file

        path = os.path.realpath(os.path.dirname(report_output))
        if not os.path.exists(path):
            os.makedirs(path)

        self.report_output = report_output

    def report(self, stream):
        self.stats['encoding'] = self.encoding
        self.stats['total'] = (self.stats['errors'] + self.stats['failures']
                               + self.stats['passes'] + self.stats['skipped'])

        with codecs.open(
            self.report_output, 'w', self.encoding, 'replace'
        ) as fp:
            fp.write(simplejson.dumps({
                'stats': self.stats,
                'results': self.results,
            }))

    def startTest(self, test):
        self._timer = time()
        self._tsc_start = self._get_tsc_timestamp()

    def external_id(self, test):
        if hasattr(test.test, 'test'):
            return getattr(test.test.test, 'test_id', None)
        else:
            return None

    def addError(self, test, err, capt=None):
        taken = self._get_time_taken()

        if issubclass(err[0], SkipTest):
            type = 'skipped'
            self.stats['skipped'] += 1
        else:
            type = 'error'
            self.stats['errors'] += 1
        tb = ''.join(traceback.format_exception(*err))
        id = test.id()
        self.results.append({
            'classname': ':'.join(id_split(id)[0].rsplit('.', 1)),
            'name': id_split(id)[-1],
            'id': self.external_id(test),
            'time': taken,
            'type': type,
            'errtype': nice_classname(err[0]),
            'message': exc_message(err),
            'tb': tb,
            'start': self._tsc_start,
            'end': self._get_tsc_timestamp(),
        })

    def addFailure(self, test, err, capt=None, tb_info=None):
        taken = self._get_time_taken()
        tb = ''.join(traceback.format_exception(*err))
        self.stats['failures'] += 1
        id = test.id()
        self.results.append({
            'classname': ':'.join(id_split(id)[0].rsplit('.', 1)),
            'name': id_split(id)[-1],
            'id': self.external_id(test),
            'time': taken,
            'type': 'failure',
            'errtype': nice_classname(err[0]),
            'message': exc_message(err),
            'tb': tb,
            'start': self._tsc_start,
            'end': self._get_tsc_timestamp(),
        })

    def addSuccess(self, test, capt=None):
        details = None
        taken = self._get_time_taken()
        self.stats['passes'] += 1
        id = test.id()
        test_result = {
            'classname': ':'.join(id_split(id)[0].rsplit('.', 1)),
            'name': id_split(id)[-1],
            'id': self.external_id(test),
            'time': taken,
            'type': 'success',
            'start': self._tsc_start,
            'end': self._get_tsc_timestamp(),
        }

        # unittest.TestCase based test
        if hasattr(test.test, 'details'):
            details = test.test.details

        # Function based test
        if details is None and hasattr(test.test, 'test'):
            if hasattr(test.test.test, 'details'):
                details = test.test.test.details

        if details is not None:
            test_result.update({'details': details})

        self.results.append(test_result)
