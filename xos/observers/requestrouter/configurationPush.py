import ansible.playbook
import ansible.constants as C
import ansible.utils.template
from ansible import errors
from ansible import callbacks
from ansible import utils
from subprocess import call

class ConfigurationPush:
	def __init__(self):
		pass

	def config_push(self, service_name, user, playbook_name,hostfile):
		'''stats = callbacks.AggregateStats()
		playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
		runner_cb = callbacks.PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)
		pb = ansible.playbook.PlayBook(playbook="playbook/site.yml",
					callbacks=playbook_cb,
            				runner_callbacks=runner_cb,
            				stats=stats
					)
		result = pb.run()
		print result
		'''

		call("ansible-playbook --private-key=planetw "+playbook_name+" -i "+hostfile+" -u "+user+"  --extra-vars \"name="+service_name+"\"", shell=True)
	

if __name__ == "__main__":
        main()
