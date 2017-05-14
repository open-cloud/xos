import unittest
import shutil
import os
from generator import *

TEST_FILE = "test_file"
TEST_OUTPUT = "Do re mi fa so la ti do"

XPROTO_FILE = 'test.xproto'
OUTPUT_FILE = 'test.output'
TARGET_FILE = 'test.xtarget'
XPROTO_DIR = "/tmp/xproto-tests"

TEST_PATH = '/'.join([XPROTO_DIR, TEST_FILE])
XPROTO_PATH = '/'.join([XPROTO_DIR, XPROTO_FILE])
TARGET_PATH = '/'.join([XPROTO_DIR, TARGET_FILE])
OUTPUT_PATH = '/'.join([XPROTO_DIR, OUTPUT_FILE])

class FakeArgs:
    pass

class XProtoTest(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(XPROTO_DIR):
            os.mkdir(XPROTO_DIR)
        open('/'.join([XPROTO_DIR, TEST_FILE]),'w').write(TEST_OUTPUT)
	#print "Test %s Started" % (self.id())


    def tearDown(self):
        #if os.path.exists(XPROTO_DIR):
        #   shutil.rmtree(XPROTO_DIR)
	pass

    def generate(self, xproto = None, target = None, kv = '', rev = False):
        if (not xproto):
            xproto = \
"""
    message X(Y) {}
"""
            pass

        if (not target):
            target = '{{ proto }}'

        target+='\n+++ %s'%OUTPUT_PATH

        open(TARGET_PATH, 'w').write(target)
        open(XPROTO_PATH, 'w').write(xproto)

        args = FakeArgs()
        args.template_dir = XPROTO_DIR
	args.quiet = True
        args.rev = rev
	args.kv = kv
        args.attic = XPROTO_DIR
        args.input = XPROTO_PATH
        args.output = OUTPUT_PATH
        args.target = TARGET_FILE
        g = XOSGenerator(args)
        g.generate()
    
    def get_output(self):
        return open(OUTPUT_PATH).read()
