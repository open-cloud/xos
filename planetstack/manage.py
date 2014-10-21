#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "planetstack.settings")

    from django.core.management import execute_from_command_line

    if "--nomodelpolicy" in sys.argv:
        import model_policy
        model_policy.EnableModelPolicy(False)
        sys.argv.remove("--nomodelpolicy")

    execute_from_command_line(sys.argv)
