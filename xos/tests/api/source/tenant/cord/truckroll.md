# Group Truckroll

Virtual Truckroll, enable to perform basic test on user connectivity such as ping, traceroute and tcpdump.

## Truckroll Collection [/api/tenant/truckroll/]

### List all Truckroll [GET]

+ Response 200 (application/json)

        [
            {
                "humanReadableName": "vTR-tenant-9",
                "id": 9,
                "provider_service": 6,
                "target_id": 2,
                "scope": "container",
                "test": "ping",
                "argument": "8.8.8.8",
                "result": "",
                "result_code": "",
                "is_synced": false,
                "backend_status": "2 - Exception('Unreachable results in ansible recipe',)"
            }
        ]

### Create a Truckroll [POST]

+ Request (application/json)

        {
            "target_id": 2,
            "scope": "container",
            "test": "ping",
            "argument": "8.8.8.8"
        }

+ Response 201 (application/json)

        {
            "humanReadableName": "vTR-tenant-1",
            "id": 1,
            "provider_service": 6,
            "target_id": 2,
            "scope": "container",
            "test": "ping",
            "argument": "8.8.8.8",
            "result": null,
            "result_code": null,
            "is_synced": false,
            "backend_status": "0 - Provisioning in progress"
        }

## Truckroll Detail [/api/tenant/truckroll/{truckroll_id}/]

A virtual truckroll is complete once is_synced equal true

+ Parameters
    + truckroll_id: 1 (number) - ID of the Truckroll in the form of an integer

### View a Truckroll Detail [GET]

+ Response 200 (application/json)

        {
            "humanReadableName": "vTR-tenant-10",
            "id": 10,
            "provider_service": 6,
            "target_id": 2,
            "scope": "container",
            "test": "ping",
            "argument": "8.8.8.8",
            "result": null,
            "result_code": null,
            "is_synced": false,
            "backend_status": "0 - Provisioning in progress"
        }

### Delete a Truckroll Detail [DELETE]

+ Response 204
