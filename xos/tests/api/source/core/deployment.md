# Group Deployments

List of the XOS deployments

## Deployments [/api/core/deployments/{id}/]

### List all deployments [GET]

+ Response 200 (application/json)

        [
            {
                "humanReadableName": "MyDeployment",
                "id": 1,
                "created": "2016-04-29T16:19:03.549901Z",
                "updated": "2016-04-29T16:19:05.624151Z",
                "enacted": null,
                "policed": null,
                "backend_register": "{}",
                "backend_status": "0 - Provisioning in progress",
                "deleted": false,
                "write_protect": false,
                "lazy_blocked": false,
                "no_sync": true,
                "name": "MyDeployment",
                "accessControl": "allow all",
                "images": [
                    "1"
                ],
                "sites": [
                    "1"
                ],
                "flavors": [
                    "1",
                    "2",
                    "3"
                ],
                "dashboardviews": [
                    "1"
                ]
            }
        ]

### Create a deployment [POST]

+ Request (application/json)

        {
            "humanReadableName": "MyDeployment",
        }

+ Response 200 (application/json)

        {
            "humanReadableName": "MyDeployment",
            "id": 1,
            "created": "2016-04-29T16:19:03.549901Z",
            "updated": "2016-04-29T16:19:05.624151Z",
            "enacted": null,
            "policed": null,
            "backend_register": "{}",
            "backend_status": "0 - Provisioning in progress",
            "deleted": false,
            "write_protect": false,
            "lazy_blocked": false,
            "no_sync": true,
            "name": "MyDeployment",
            "accessControl": "allow all",
            "images": [
                "1"
            ],
            "sites": [
                "1"
            ],
            "flavors": [
                "1",
                "2",
                "3"
            ],
            "dashboardviews": [
                "1"
            ]
        }

### View a Deployment Detail [GET]

+ Parameters
    + id: 1 (number) - ID of the Deployment in the form of an integer

+ Response 200 (application/json)

        {
            "humanReadableName": "MyDeployment",
            "id": 1,
            "created": "2016-04-27T21:46:57.354544Z",
            "updated": "2016-04-27T21:47:05.221720Z",
            "enacted": null,
            "policed": null,
            "backend_register": "{}",
            "backend_status": "0 - Provisioning in progress",
            "deleted": false,
            "write_protect": false,
            "lazy_blocked": false,
            "no_sync": true,
            "name": "MyDeployment",
            "accessControl": "allow all",
            "images": [],
            "sites": [
                "1"
            ],
            "flavors": [
                "3",
                "2",
                "1"
            ],
            "dashboardviews": [
                "3"
            ]
        }

### Delete a Deployment [DELETE]

+ Parameters
    + id: 1 (number) - ID of the Deployment in the form of an integer

+ Response 204