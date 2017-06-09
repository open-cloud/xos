import os

# Constants
OUTPUT_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/out/")

TMP_TARGET_PATH = os.path.join(OUTPUT_DIR, 'tmp.xtarget')

# Store in this class the args to pass at the generator
class FakeArgs:
    pass

class XProtoTestHelpers:

    @staticmethod
    def write_tmp_target(target):
        tmp_file = open(TMP_TARGET_PATH, 'w')
        tmp_file.write(target)
        tmp_file.close()
        return TMP_TARGET_PATH

