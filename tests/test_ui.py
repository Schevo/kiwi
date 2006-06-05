import os
import sys
import traceback
import unittest
import popen2

def setup(self, rootdir):
    self._dir = os.getcwd()
    os.chdir(rootdir)

def teardown(self):
    os.chdir(self._dir)

def test_filename(rootdir, filename):
    cmd = '%s %s %s' % (sys.executable,
                        os.path.join(rootdir, 'bin', 'kiwi-ui-test'),
                        os.path.join('tests', 'ui', filename))
    if sys.platform == 'win32':
        status = os.system(cmd)
    else:
        p = popen2.Popen3(cmd)
        status = os.waitpid(p.pid, 0)[1]

    if status != 0:
        raise AssertionError("UI Test %s failed" % filename)

def create():
    testdir = os.path.dirname(__file__)
    uidir = os.path.join(testdir, 'ui')
    rootdir = os.path.dirname(testdir)

    tests = {}
    tests['setUp'] = lambda self, rootdir=rootdir: setup(self, rootdir)
    tests['tearDown'] = lambda self, rootdir=rootdir: teardown(self)

    for filename in os.listdir(uidir):
        if not filename.endswith('.py'):
            continue
        name = 'test_' + filename[:-3]

        full = os.path.join(uidir, filename)

        func = lambda self, filename=filename: test_filename(rootdir, filename)
        try:
            func.__name__ = name
        except TypeError:
            pass
        tests[name] = func

    return type('TestUI', (unittest.TestCase,), tests)

# Disable UI tests on win32, they do not quite work yet.
if sys.platform != 'win32':
    TestUI = create()

