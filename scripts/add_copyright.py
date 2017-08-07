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

import sys
import os

COPYRIGHTS = {
    "slash": """
/*
 * Copyright 2017-present Open Networking Foundation

 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at

 * http://www.apache.org/licenses/LICENSE-2.0

 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
""",
    "hash": """
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
""",
    "html": """
<!--
Copyright 2017-present Open Networking Foundation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->
""",
    "jinja": """
{#
Copyright 2017-present Open Networking Foundation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
#}
""",
    "ini": """
;Copyright 2017-present Open Networking Foundation
;
;Licensed under the Apache License, Version 2.0 (the "License");
;you may not use this file except in compliance with the License.
;You may obtain a copy of the License at
;
;http://www.apache.org/licenses/LICENSE-2.0
;
;Unless required by applicable law or agreed to in writing, software
;distributed under the License is distributed on an "AS IS" BASIS,
;WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
;See the License for the specific language governing permissions and
;limitations under the License.
""",
}

EXT_MAPPING = {
    ".js": COPYRIGHTS["slash"],
    ".ts": COPYRIGHTS["slash"],
    ".scss": COPYRIGHTS["slash"],
    ".css": COPYRIGHTS["slash"],
    ".gradle": COPYRIGHTS["slash"],

    "docker": COPYRIGHTS["hash"],
    ".py": COPYRIGHTS["hash"],
    ".model": COPYRIGHTS["hash"], # attic files
    ".sh": COPYRIGHTS["hash"],
    ".yaml": COPYRIGHTS["hash"],
    ".yml": COPYRIGHTS["hash"],
    ".m4": COPYRIGHTS["hash"],
    ".sql": COPYRIGHTS["hash"],

    ".html": COPYRIGHTS["html"],
    ".j2": COPYRIGHTS["jinja"],
    ".ini": COPYRIGHTS["ini"],
}

def get_copyright(file):
    name, ext = os.path.splitext(file)

    if "Dockerfile" in name:
        return EXT_MAPPING["docker"]
    try:
        return EXT_MAPPING[ext]
    except KeyError, e:
        print "Missing copyright for file of type: %s" % ext
        return None

def add_copyright(file):
    with open(file, 'r') as original: data = original.read()
    if not "Copyright 2017-present Open Networking Foundation" in data:
        print "Adding copyright to: %s" % file

        copy = get_copyright(file)
        if copy:
            with open(file, 'w') as modified: modified.write(copy + "\n\n" + data)
    return

def get_files_ignore_by_git(root):
    # NOTE this is not perfect, some file will still be copyrighted, but we save some time
    if root == ".gitignore":
        gitignore = root
    else:
        gitignore = os.path.join(root, ".gitignore")

    exclusion_list = []
    if os.path.exists(gitignore):
        for line in open(gitignore).readlines():
            if not "#" in line:
                line = line.strip()
                if line.endswith("/"):
                    line = line.replace("/", "")
                exclusion_list.append(line)
    return exclusion_list

def should_skip(entry):

    # do not skip directories
    if os.path.isdir(entry):
        return False

    if "LICENSE.txt" in entry \
    or ".git" in entry \
    or ".idea" in entry:
        return True

    name, ext = os.path.splitext(entry)
    if not ext or ext == "" \
    or ext ==".pyc" \
    or ext == ".txt" \
    or ext == ".in" \
    or ext == ".crt" \
    or ext == ".unused" \
    or ext == ".list" \
    or ext == ".README" \
    or ext == ".json" \
    or ext == ".log" \
    or ext == ".asc" \
    or ext == ".dot" \
    or ext == ".do" \
    or ext == ".template" \
    or ext == ".svg" \
    or ext == ".ttf" \
    or ext == ".woff" \
    or ext == ".woof2" \
    or ext == ".eot" \
    or ext == ".md" \
    or ext == ".png" \
    or ext == ".PNG" \
    or ext == ".jpg" \
    or ext == ".gif" \
    or ext == ".ico" \
    or ext == ".conf"\
    or ext == ".key" \
    or ext == ".proto" \
    or ext == ".xproto" \
    or ext == ".xtarget" \
    or ext == ".otf" \
    or ext == ".desc":
        return True
    return False

def recursive_iterate_dirs(source, apply_copyright=True):
    # print "Iteranting on: %s" % source
    # skipping files in the gitignore
    gitignored = get_files_ignore_by_git(source)
    entries = []
    for entry in os.listdir(source):

        if entry in gitignored:
            # print "Skipping because gitignored: %s" % entry
            continue

        entry = os.path.join(source, entry)
        if should_skip(entry):
            # print "Skipping: %s" % entry
            continue

        if os.path.isdir(entry):
            entries.append(recursive_iterate_dirs(entry, apply_copyright))
        elif os.path.isfile(entry):
            entries.append(entry)
            if apply_copyright is True:
                add_copyright(entry)
    return entries

def flatten(aList):
    t = []
    for i in aList:
        if not isinstance(i, list):
             t.append(i)
        else:
             t.extend(flatten(i))
    return t

def list_file_types(source):
    file_types = []
    files = flatten(recursive_iterate_dirs(source, apply_copyright=False))
    for entry in files:
        name, ext = os.path.splitext(entry)
        if not ext in file_types:
            file_types.append(ext)
    print file_types

def main():
    if len(sys.argv) < 2:
        raise Exception("You must provide a path to the source folder as arguments to the script")
    source_root = os.path.abspath(os.path.join(os.getcwd(), sys.argv[1]))
    if not os.path.exists(source_root):
        raise Exception("You must provide an existing the source folder")
    if len(sys.argv) == 3:
        list_file_types(source_root)
    else:
        recursive_iterate_dirs(source_root)


if __name__ == "__main__":
    main()