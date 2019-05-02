# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
  This module is used to validate xproto models and fields. The basic guiding principle is everything that isn't
  specifically allowed here should be denied by default.

  Note: While xproto must maintain some compatibility with django give the implementation choice of using django
  in the core, it's the case that the allowable set of xproto options may be a subset of what is allowed under
  django. For example, there may be django features that do not need exposure in xproto and/or are incompatible
  with other design aspects of XOS such as the XOS gRPC API  implementation.
"""

from __future__ import print_function
import sys
import os


# Options that are always allowed
COMMON_OPTIONS = ["help_text", "gui_hidden", "tosca_key", "tosca_key_one_of",
                  "bookkeeping_state", "feedback_state", "unique", "unique_with"]

# Options that must be either "True" or "False"
BOOLEAN_OPTIONS = ["blank", "db_index", "bookkeeping_state", "feedback_state", "gui_hidden", "null",
                   "tosca_key", "unique", "text"]


class XProtoValidator(object):
    def __init__(self, models, line_map):
        """
            models: a list of model definitions. Each model is a dictionary.
            line_map: a list of tuples (start_line_no, filename) that tells which file goes with which line number.
        """
        self.models = models
        self.line_map = line_map
        self.errors = []

    def error(self, model, field, message, severity="ERROR"):
        if field and field.get("_linespan"):
            error_first_line_number = field["_linespan"][0]
            error_last_line_number = field["_linespan"][1]
        else:
            error_first_line_number = model["_linespan"][0]
            error_last_line_number = model["_linespan"][1]

        error_filename = "unknown"
        error_line_offset = 0
        for (start_line, fn) in self.line_map:
            if start_line > error_first_line_number:
                break
            error_filename = fn
            error_line_offset = start_line

        self.errors.append({"severity": severity,
                            "model": model,
                            "field": field,
                            "message": message,
                            "filename": error_filename,
                            "first_line_number": error_first_line_number - error_line_offset,
                            "last_line_number": error_last_line_number - error_line_offset,
                            "absolute_line_number": error_first_line_number})

    def warning(self, *args, **kwargs):
        self.error(*args, severity="WARNING", **kwargs)

    def print_errors(self):
        # Sort by line number
        for error in sorted(self.errors, key=lambda error: error["absolute_line_number"]):
            model = error["model"]
            field = error["field"]
            message = error["message"]
            first_line_number = error["first_line_number"]
            last_line_number = error["last_line_number"]

            if first_line_number != last_line_number:
                linestr = "%d-%d" % (first_line_number, last_line_number)
            else:
                linestr = "%d" % first_line_number

            print("[%s] %s:%s %s.%s (Type %s): %s" % (error["severity"],
                                                      os.path.basename(error["filename"]),
                                                      linestr,
                                                      model.get("name"),
                                                      field.get("name"),
                                                      field.get("type"),
                                                      message), file=sys.stderr)

    def is_option_true(self, field, name):
        options = field.get("options")
        if not options:
            return False
        option = options.get(name)
        return option == "True"

    def allow_options(self, model, field, options):
        """ Only allow the options specified in `options`. If some option is present that isn't in allowed, then
            register an error.

            `options` is a list of options which can either be simple names, or `name=value`.
        """
        options = COMMON_OPTIONS + options

        for (k, v) in field.get("options", {}).items():
            allowed = False
            for option in options:
                if "=" in option:
                    (optname, optval) = option.split("=")
                    if optname == k and optval == v:
                        allowed = True
                else:
                    if option == k:
                        allowed = True

            if not allowed:
                self.error(model, field, "Option %s=%s is not allowed" % (k, v))

            if k in BOOLEAN_OPTIONS and (v not in ["True", "False"]):
                self.error(model, field, "Option `%s` must be either True or False, but is '%s'" % (k, v))

    def require_options(self, model, field, options):
        """ Require an option to be present.
        """
        options = field.get("options", {})
        for optname in options:
            if optname not in options:
                self.error(model, field, "Required option '%s' is not present" % optname)

    def check_modifier_consistent(self, model, field):
        """ Validates that "modifier" is consistent with options.

            Required/optional imply some settings for blank= and null=. These settings are dependent on the type
            of field. See also jinja2_extensions/django.py which has to implement some of the same logic.
        """
        field_type = field["type"]
        options = field.get("options", {})
        modifier = options.get('modifier')
        link_type = field.get("link_type")
        mod_out = {}

        if modifier == "required":
            mod_out["blank"] = 'False'

            if link_type != "manytomany":
                mod_out["null"] = 'False'

        elif modifier == "optional":
            mod_out["blank"] = 'True'

            # set defaults on link types
            if link_type != "manytomany" and field_type != "bool":
                mod_out["null"] = 'True'

        else:
            self.error(model, field, "Unknown modifier type '%s'" % modifier)

        # print an error if there's a field conflict
        for kmo in mod_out.keys():
            if (kmo in options) and (options[kmo] != mod_out[kmo]):
                self.error(model, field, "Option `%s`=`%s` is inconsistent with modifier `%s`" %
                           (kmo, options[kmo], modifier))

    def validate_field_date(self, model, field):
        self.check_modifier_consistent(model, field)
        self.allow_options(model, field,
                           ["auto_now_add", "blank", "db_index", "default",
                            "max_length", "modifier", "null", "content_type"])

    def validate_field_string(self, model, field):
        # A string with a `content_type="date"` is actually a date
        # TODO: Investigate why there are double-quotes around "date"
        content_type = field.get("options", {}).get("content_type")
        if content_type in ["\"date\""]:
            self.validate_field_date(model, field)
            return

        # TODO: Investigate why there are double-quotes around the content types
        if content_type and content_type not in ["\"stripped\"", "\"ip\"", "\"url\""]:
            self.error(model, field, "Content type %s is not allowed" % content_type)

        self.check_modifier_consistent(model, field)
        self.allow_options(model, field,
                           ["blank", "choices", "content_type", "db_index", "default",
                            "max_length", "modifier", "null", "text"])

        # max_length is a mandatory argument of CharField.
        if (content_type in [None]) and \
           (not self.is_option_true(field, "text")) and \
           ("max_length" not in field["options"]):
            self.error(model, field, "String field should have a max_length or text=True")

        if "max_length" in field["options"]:
            max_length = field["options"]["max_length"]
            try:
                max_length = int(max_length)
                if (max_length == 0):
                    self.error(model, field, "max_length should not be zero")

                if 0 < abs(256-max_length) < 3:
                    self.warning(model, field,
                                 "max_length of %s is close to suggested max_length of 256" % max_length)

                if 0 < abs(1024-max_length) < 3:
                    self.warning(model, field,
                                 "max_length of %s is close to suggested max_length of 1024" % max_length)
            except ValueError:
                self.error(model, field, "max_length must be a number")

    def validate_field_bool(self, model, field):
        self.check_modifier_consistent(model, field)
        self.allow_options(model, field, ["db_index", "default=True", "default=False", "modifier", "null=False"])
        self.require_options(model, field, ["default"])

    def validate_field_float(self, model, field):
        self.check_modifier_consistent(model, field)
        self.allow_options(model, field, ["blank", "db_index", "default", "modifier", "null"])

    def validate_field_link_onetomany(self, model, field):
        self.check_modifier_consistent(model, field)
        self.allow_options(model, field,
                           ["blank", "db_index", "default", "model", "link_type=manytoone",
                            "modifier", "null", "port", "type=link"])

    def validate_field_link_manytomany(self, model, field):
        self.check_modifier_consistent(model, field)
        self.allow_options(model, field,
                           ["blank", "db_index", "default", "model", "link_type=manytomany",
                            "modifier", "null", "port", "type=link"])

    def validate_field_link(self, model, field):
        link_type = field.get("options", {}).get("link_type")
        if link_type == "manytoone":
            self.validate_field_link_onetomany(model, field)
        elif link_type == "manytomany":
            self.validate_field_link_manytomany(model, field)
        else:
            self.error(model, field, "Unknown link_type %s" % link_type)

    def validate_field_integer(self, model, field):
        # An integer with an option "type=link" is actually a link
        if field.get("options", {}).get("type") == "link":
            self.validate_field_link(model, field)
            return

        self.check_modifier_consistent(model, field)
        self.allow_options(model, field,
                           ["blank", "db_index", "default", "max_value", "min_value", "modifier", "null"])

        if self.is_option_true(field, "blank") and not self.is_option_true(field, "null"):
            self.error(model, field, "If blank is true then null must also be true")

    def validate_field(self, model, field):
        if field["type"] == "string":
            self.validate_field_string(model, field)
        elif field["type"] in ["int32", "uint32"]:
            self.validate_field_integer(model, field)
        elif field["type"] == "float":
            self.validate_field_float(model, field)
        elif field["type"] == "bool":
            self.validate_field_bool(model, field)
        else:
            self.error(model, field, "Unknown field type %s" % field["type"])

    def validate_model(self, model):
        for field in model["fields"]:
            self.validate_field(model, field)

    def validate(self):
        """ Validate all models. This is the main entrypoint for validating xproto. """
        for (name, model) in self.models.items():
            self.validate_model(model)
