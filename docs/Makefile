DOCSDIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

swagger: swagger_clean swagger_docs swagger_serve_spec

venv-xosdocs:
	bash venv-xosdocs.sh

swagger_docs: venv-xosdocs
	bash -c 'source $(DOCSDIR)venv-xosdocs/bin/activate && python $(DOCSDIR)scripts/swagger_docs.py'

swagger_clean:
	rm -rf swagger/specs/*

venv_clean:
	rm -rf $(DOCSDIR)venv-xosdocs

swagger_serve_spec:
	http-server --cors ./swagger

# HOW TO
# - load the virtual env (https://guide.opencord.org/xos/dev/local_env.html)
# - run `make`
# - open the browser at `http://127.0.0.1:8080/ui`
# - you'll see the 'core' apis
# - you can see a list of available apis at `http://127.0.0.1:8080/specs/`
# - just replace the swagger file (top bar) with another one to see different APIs (to be improved)
