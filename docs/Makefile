swagger: swagger_clean swagger_docs swagger_serve_spec

swagger_docs:
	python scripts/swagger_docs.py

swagger_clean:
	rm -rf swagger/specs/*

swagger_serve_spec:
	http-server --cors ./swagger

# HOW TO
# - load the virtual env (https://guide.opencord.org/xos/dev/local_env.html)
# - run `make`
# - open the browser at `http://127.0.0.1:8080/ui`
# - you'll see the 'core' apis
# - you can see a list of available apis at `http://127.0.0.1:8080/specs/`
# - just replace the swagger file (top bar) with another one to see different APIs (to be improved)
