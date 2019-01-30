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

from __future__ import absolute_import

import os
import pickle
import sys
import traceback

from xosconfig import Config

try:
    # Python 2: "reload" is built-in
    reload  # pylint: disable=reload-builtin
except NameError:
    from importlib import reload

sys.path.append("/opt/xos")


def run_playbook(ansible_hosts, ansible_config, fqp, opts):
    try:
        if ansible_config:
            os.environ["ANSIBLE_CONFIG"] = ansible_config
        else:
            try:
                del os.environ["ANSIBLE_CONFIG"]
            except KeyError:
                pass

        if ansible_hosts:
            os.environ["ANSIBLE_HOSTS"] = ansible_hosts
        else:
            try:
                del os.environ["ANSIBLE_HOSTS"]
            except KeyError:
                pass

        from . import ansible_runner

        reload(ansible_runner)

        # Dropped support for observer_pretend - to be redone
        runner = ansible_runner.Runner(
            playbook=fqp, run_data=opts, host_file=ansible_hosts
        )

        stats, aresults = runner.run()
    except Exception:
        return {"stats": None, "aresults": None, "exception": traceback.format_exc()}

    return {"stats": stats, "aresults": aresults}


def main():
    input_fn = sys.argv[1]
    result_fn = sys.argv[2]

    args = pickle.loads(open(input_fn).read())

    Config.init(args["config_file"], "synchronizer-config-schema.yaml")

    ansible_hosts = args["ansible_hosts"]
    ansible_config = args["ansible_config"]
    fqp = args["fqp"]
    opts = args["opts"]

    result = run_playbook(ansible_hosts, ansible_config, fqp, opts)

    open(result_fn, "w").write(pickle.dumps(result))


if __name__ == "__main__":
    main()
