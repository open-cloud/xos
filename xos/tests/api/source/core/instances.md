# Group Instances

List of the XOS instances

## Instances Collection [/api/core/instances/{?no_hyperlinks}]

    + no_hyperlinks (number, optional) - Wheter to return relation with links or ids
        + Default: `0`

### List all Instances [GET]

+ Response 200 (application/json)

        [
            {
                "id": 1,
                "humanReadableName": "uninstantiated-1",
                "created": "2016-04-26T00:36:22.465259Z",
                "updated": "2016-04-26T00:36:22.465288Z",
                "enacted": null,
                "policed": null,
                "backend_register": "{}",
                "backend_status": "0 - Provisioning in progress",
                "deleted": false,
                "write_protect": false,
                "lazy_blocked": false,
                "no_sync": false,
                "instance_id": null,
                "instance_uuid": null,
                "name": "mysite_vcpe",
                "instance_name": null,
                "ip": null,
                "image": "1",
                "creator": "1",
                "slice": "1",
                "deployment": "1",
                "node": "1",
                "numberCores": 0,
                "flavor": "1",
                "userData": null,
                "isolation": "vm",
                "volumes": "/etc/dnsmasq.d,/etc/ufw",
                "parent": null,
                "networks": [
                    "1"
                ]
            }
        ]

### Create an Instance [POST]

+ Parameters
    + no_hyperlinks: 1

+ Request (application/json)

        {
            "name": "test-instance",
            "image": 1,
            "slice": 1,
            "deployment": 1,
            "node": 1
        }

+ Response 200 (application/json)

        {
            "id": 1,
            "humanReadableName": "uninstantiated-1",
            "created": "2016-04-26T00:36:22.465259Z",
            "updated": "2016-04-26T00:36:22.465288Z",
            "enacted": null,
            "policed": null,
            "backend_register": "{}",
            "backend_status": "0 - Provisioning in progress",
            "deleted": false,
            "write_protect": false,
            "lazy_blocked": false,
            "no_sync": false,
            "instance_id": null,
            "instance_uuid": null,
            "name": "test-instance",
            "instance_name": null,
            "ip": null,
            "image": "1",
            "creator": "1",
            "slice": "1",
            "deployment": "1",
            "node": "1",
            "numberCores": 0,
            "flavor": "1",
            "userData": null,
            "isolation": "vm",
            "volumes": "/etc/dnsmasq.d,/etc/ufw",
            "parent": null,
            "networks": [
                "1"
            ]
        }

## Instances Detail [/api/core/instances/{id}/]

### Get instance details [GET]

+ Parameters
    + id: 1 (number) - ID of the Instance in the form of an integer

+ Response 200 (application/json)

        {
            "id": 1,
            "humanReadableName": "uninstantiated-1",
            "created": "2016-04-26T00:36:22.465259Z",
            "updated": "2016-04-26T00:36:22.465288Z",
            "enacted": null,
            "policed": null,
            "backend_register": "{}",
            "backend_status": "0 - Provisioning in progress",
            "deleted": false,
            "write_protect": false,
            "lazy_blocked": false,
            "no_sync": false,
            "instance_id": null,
            "instance_uuid": null,
            "name": "mysite_vcpe",
            "instance_name": null,
            "ip": null,
            "image": "1",
            "creator": "1",
            "slice": "1",
            "deployment": "1",
            "node": "1",
            "numberCores": 0,
            "flavor": "1",
            "userData": null,
            "isolation": "vm",
            "volumes": "/etc/dnsmasq.d,/etc/ufw",
            "parent": null,
            "networks": [
                "1"
            ]
        }

### Delete instance [DELETE]

+ Parameters
    + id: 1 (number) - ID of the Instance in the form of an integer

+ Response 204