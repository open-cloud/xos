source /opt/xos/grpc/tests/chamconfig.sh

# test modeldefs
curl -f --silent http://$HOSTNAME:8080/xosapi/v1/modeldefs > /dev/null
if [[ $? -ne 0 ]]; then
    echo fail modeldefs
fi

{% for object in generator.all() %}
curl -f --silent http://$HOSTNAME:8080/xosapi/v1/{{ object.camel()|lower }}s > /dev/null
if [[ $? -ne 0 ]]; then
    echo fail {{ object.camel() }}
fi
{%- endfor %}

echo "okay"

