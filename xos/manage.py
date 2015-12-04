#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")

    from django.core.management import execute_from_command_line

    if "--makemigrations" in sys.argv:
        os.system("/opt/xos/scripts/opencloud makemigrations")
        sys.argv.remove("--makemigrations")

    if "--nomodelpolicy" in sys.argv:
        import model_policy
        model_policy.EnableModelPolicy(False)
        sys.argv.remove("--nomodelpolicy")

    if "--noobserver" in sys.argv:
        import observer
        observer.EnableObserver(False)
        sys.argv.remove("--noobserver")

    execute_from_command_line(sys.argv)
