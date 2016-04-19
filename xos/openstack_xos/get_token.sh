curl --insecure -i -X POST $ENDPOINT/auth/tokens \
  -H "Content-type: application/json" \
  -d '
{ "auth": {
    "identity": {
      "methods": ["password"],
      "password": {
        "user": {
          "name": "'$USERNAME'",
          "domain": { "id": "'$DOMAIN'" },
          "password": "'$PASSWORD'"
        }
      }
    },
    "scope": {
      "project": {
        "name": "'$TENANT'",
        "domain": { "id": "'$DOMAIN'" }
      }
    }
  }
}' \
  | grep X-Subject-Token | awk '{print $2;}'
