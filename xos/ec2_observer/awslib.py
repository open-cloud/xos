import os
import json

class AwsException(Exception):
	pass

def aws_run(cmd,env=''):
	cmd = '%s aws %s'%(env,cmd)
	pipe = os.popen(cmd)
	output_str = pipe.read()

	if (not pipe.close()):
		output = json.loads(output_str)
		return output
	else:
		raise AwsException("Error: %s"%output_str)


