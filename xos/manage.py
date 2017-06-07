#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.chdir('..')  # <<<---This is what you want to add
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")

    from django.core.management import execute_from_command_line

    if "--makemigrations" in sys.argv:
        os.system("/opt/xos/tools/xos-manage makemigrations")
        sys.argv.remove("--makemigrations")

    execute_from_command_line(sys.argv)
