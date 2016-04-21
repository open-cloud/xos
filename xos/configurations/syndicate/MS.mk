# MS build parameters

MS_APP_ADMIN_EMAIL        ?= sites@opencloud.us
MS_APP_PUBLIC_HOST				?= localhost
MS_APP_ADMIN_PUBLIC_KEY   ?= ms/admin.pub
MS_APP_ADMIN_PRIVATE_KEY  ?= ms/admin.pem

MS_APP_NAME               ?= syndicate-ms
MS_APP_PUBLIC_KEY         ?= ms/syndicate.pub
MS_APP_PRIVATE_KEY        ?= ms/syndicate.pem

MS_DEVEL                  ?= true

$(MS_APP_ADMIN_PRIVATE_KEY):
	openssl genrsa 4096 > "$@"

$(MS_APP_ADMIN_PUBLIC_KEY): $(MS_APP_ADMIN_PRIVATE_KEY)
	openssl rsa -in "$<" -pubout > "$@"

$(MS_APP_PRIVATE_KEY):
	openssl genrsa 4096 > "$@"

$(MS_APP_PUBLIC_KEY): $(MS_APP_PRIVATE_KEY)
	openssl rsa -in "$<" -pubout > "$@"

ms/admin_info.py: ms/admin_info.pyin $(MS_APP_ADMIN_PUBLIC_KEY) $(MS_APP_PUBLIC_KEY) $(MS_APP_PRIVATE_KEY)
	mkdir -p "$(@D)"
	cat "$<" | \
		sed -e 's~@MS_APP_NAME@~$(MS_APP_NAME)~g;' | \
		sed -e 's~@MS_APP_ADMIN_EMAIL@~$(MS_APP_ADMIN_EMAIL)~g;' | \
		sed -e 's~@MS_DEVEL@~$(MS_DEVEL)~g;' | \
		sed -e 's~@MS_APP_ADMIN_PUBLIC_KEY@~$(shell cat $(MS_APP_ADMIN_PUBLIC_KEY) | tr "\n" "@" | sed 's/@/\\n/g')~g;' | \
		sed -e 's~@MS_APP_PRIVATE_KEY@~$(shell cat $(MS_APP_PRIVATE_KEY) | tr "\n" "@" | sed 's/@/\\n/g')~g;' | \
		sed -e 's~@MS_APP_PUBLIC_KEY@~$(shell cat $(MS_APP_PUBLIC_KEY) | tr "\n" "@" | sed 's/@/\\n/g')~g;' > "$@"

ms/app.yaml: ms/app.yamlin
	mkdir -p "$(@D)"
	cat "$<" | \
		sed -e 's~@MS_APP_NAME@~$(MS_APP_NAME)~g;' | \
		sed -e 's~@MS_APP_PUBLIC_HOST@~$(MS_APP_PUBLIC_HOST)~g;' > "$@"

clean: 
	rm -f ms/admin_info.py ms/app.yaml

clean_certs:
	rm -f $(MS_APP_ADMIN_PUBLIC_KEY) $(MS_APP_ADMIN_PRIVATE_KEY) $(MS_APP_PUBLIC_KEY) $(MS_APP_PRIVATE_KEY)

