# Group ONOS Apps

## ONOS App Collection [/api/tenant/onos/app/]

### List all apps [GET]

+ Response 200 (application/json)

        [
            {
                "humanReadableName": "onos-tenant-7",
                "id": 7,
                "name": "vBNG_ONOS_app",
                "dependencies": "org.onosproject.proxyarp, org.onosproject.virtualbng, org.onosproject.openflow, org.onosproject.fwd"
            }
        ]