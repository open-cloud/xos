import os
import pickle
import sys
#import json
import traceback
from xosconfig import Config

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

        import ansible_runner
        reload(ansible_runner)

        # Dropped support for observer_pretend - to be redone
        runner = ansible_runner.Runner(
            playbook=fqp,
            run_data=opts,
            host_file=ansible_hosts)

        stats,aresults = runner.run()
    except Exception, e:
        return {"stats": None, "aresults": None, "exception": traceback.format_exc()}

    return {"stats": stats, "aresults": aresults}

def main():
    input_fn = sys.argv[1]
    result_fn = sys.argv[2]

    args = pickle.loads(open(input_fn).read())

    Config.init(args['config_file'], 'synchronizer-config-schema.yaml')

    ansible_hosts = args["ansible_hosts"]
    ansible_config = args["ansible_config"]
    fqp = args["fqp"]
    opts = args["opts"]

    result = run_playbook(ansible_hosts, ansible_config, fqp, opts)

    open(result_fn, "w").write(pickle.dumps(result))

if __name__ == "__main__":
    main()
