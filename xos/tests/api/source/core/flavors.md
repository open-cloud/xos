# Group Flavors

List of the XOS flavors

## Flavors [/api/core/flavors/{id}/]

### List all flavors [GET]

+ Response 200 (application/json)

        [
            {
                "humanReadableName": "m1.large",
                "id": 1,
                 "created": "2016-04-29T16:19:01.979548Z",
                "updated": "2016-04-29T16:19:03.568238Z",
                "enacted": null,
                "policed": null,
                "backend_register": "{}",
                "backend_status": "0 - Provisioning in progress",
                "deleted": false,
                "write_protect": false,
                "lazy_blocked": false,
                "no_sync": true,
                "name": "m1.large",
                "description": null,
                "flavor": "m1.large",
                "order": 0,
                "default": false,
                "deployments": [
                    "1"
                ]
            }
        ]

### Create a Flavor [POST]

+ Request (application/json)

        {
            "humanReadableName": "mq.test",
        }

+ Response 200 (application/json)

        {
            "humanReadableName": "m1.large",
            "id": 1,
             "created": "2016-04-29T16:19:01.979548Z",
            "updated": "2016-04-29T16:19:03.568238Z",
            "enacted": null,
            "policed": null,
            "backend_register": "{}",
            "backend_status": "0 - Provisioning in progress",
            "deleted": false,
            "write_protect": false,
            "lazy_blocked": false,
            "no_sync": true,
            "name": "m1.large",
            "description": null,
            "flavor": "m1.large",
            "order": 0,
            "default": false,
            "deployments": [
                "1"
            ]
        }

### View a Flavors Detail [GET]

+ Parameters
    + id: 1 (number) - ID of the Flavors in the form of an integer

+ Response 200 (application/json)

        {
            "humanReadableName": "m1.large",
            "id": 1,
             "created": "2016-04-29T16:19:01.979548Z",
            "updated": "2016-04-29T16:19:03.568238Z",
            "enacted": null,
            "policed": null,
            "backend_register": "{}",
            "backend_status": "0 - Provisioning in progress",
            "deleted": false,
            "write_protect": false,
            "lazy_blocked": false,
            "no_sync": true,
            "name": "m1.large",
            "description": null,
            "flavor": "m1.large",
            "order": 0,
            "default": false,
            "deployments": [
                "1"
            ]
        }

### Delete a Flavors Detail [DELETE]

+ Parameters
    + id: 1 (number) - ID of the Flavors in the form of an integer

+ Response 204 