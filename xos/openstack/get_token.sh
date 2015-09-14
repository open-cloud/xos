curl --insecure -X POST $ENDPOINT/v2.0/tokens \
  -H "Content-type: application/json" \
  -d '{"auth": {"tenantName": "'$TENANT'", "passwordCredentials":{"username": "'$USERNAME'", "password": "'$PASSWORD'"}}}' \
  | python -c 'import json,sys;obj=json.load(sys.stdin);print obj["access"]["token"]["id"];'
