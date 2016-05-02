# MS configuration parameters

# Where app.yamlin can be found
CONFIG_DIR ?= .

# Output directory for app.yaml
BUILD_MS ?=

# Where to put generated pub/priv keys
KEY_FILES ?= $(CONFIG_DIR)

MS_APP_NAME			?= syndicate-ms
MS_APP_PUBLIC_HOST	?= localhost
MS_APP_ADMIN_EMAIL	?= syndicate-ms@example.com

MS_APP_ADMIN_PUBLIC_KEY		?= $(KEY_FILES)/admin.pub
MS_APP_ADMIN_PRIVATE_KEY	?= $(KEY_FILES)/admin.pem

MS_APP_PUBLIC_KEY	?= $(KEY_FILES)/syndicate.pub
MS_APP_PRIVATE_KEY	?= $(KEY_FILES)/syndicate.pem

$(MS_APP_ADMIN_PRIVATE_KEY):
	openssl genrsa 4096 > "$@"

$(MS_APP_ADMIN_PUBLIC_KEY): $(MS_APP_ADMIN_PRIVATE_KEY)
	openssl rsa -in "$<" -pubout > "$@"

$(MS_APP_PRIVATE_KEY):
	openssl genrsa 4096 > "$@"

$(MS_APP_PUBLIC_KEY): $(MS_APP_PRIVATE_KEY)
	openssl rsa -in "$<" -pubout > "$@"

$(BUILD_MS)/app.yaml: $(CONFIG_DIR)/app.yamlin $(MS_APP_ADMIN_PUBLIC_KEY) $(MS_APP_PUBLIC_KEY) $(MS_APP_PRIVATE_KEY)
	mkdir -p "$(@D)"
	cat "$<" | \
		sed -e 's~@MS_APP_NAME@~$(MS_APP_NAME)~g;' \
			-e 's~@MS_APP_PUBLIC_HOST@~$(MS_APP_PUBLIC_HOST)~g;' \
			-e 's~@MS_APP_ADMIN_EMAIL@~$(MS_APP_ADMIN_EMAIL)~g;' \
			-e 's~@MS_APP_ADMIN_PUBLIC_KEY@~$(shell cat "$(MS_APP_ADMIN_PUBLIC_KEY)" | tr "\n" "@  " | sed 's/@/\\n    /g')~g;' \
			-e 's~@MS_APP_PUBLIC_KEY@~$(shell cat "$(MS_APP_PUBLIC_KEY)" | tr "\n" "@" | sed 's/@/\\n    /g')~g;' \
			-e 's~@MS_APP_PRIVATE_KEY@~$(shell cat "$(MS_APP_PRIVATE_KEY)" | tr "\n" "@" | sed 's/@/\\n    /g')~g;' \
		> "$@"

clean_ms:
	rm -f $(BUILD_MS)/ms/app.yaml

clean_certs: clean_ms
	rm -f $(MS_APP_ADMIN_PUBLIC_KEY) $(MS_APP_ADMIN_PRIVATE_KEY) $(MS_APP_PUBLIC_KEY) $(MS_APP_PRIVATE_KEY)

