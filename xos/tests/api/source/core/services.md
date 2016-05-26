# Group Services

List of the XOS Services

## Services [/api/core/services/{id}/]

### List all Services [GET]

+ Response 200 (application/json)

        [
            {
                "humanReadableName": "MyService",
                "id": 1,
                "created": "2016-05-05T23:06:33.835277Z",
                "updated": "2016-05-05T23:06:33.835302Z",
                "enacted": null,
                "policed": null,
                "backend_register": "{}",
                "backend_status": "0 - Provisioning in progress",
                "deleted": false,
                "write_protect": false,
                "lazy_blocked": false,
                "no_sync": false,
                "no_policy": false,
                "description": null,
                "enabled": true,
                "kind": "vROUTER",
                "name": "MyService",
                "versionNumber": null,
                "published": true,
                "view_url": "/admin/vrouter/vrouterservice/$id$/",
                "icon_url": null,
                "public_key": null,
                "private_key_fn": null,
                "service_specific_id": null,
                "service_specific_attribute": null
            }
        ]

### Create a Service [POST]

+ Request (application/json)

        {
            "name": "MyService",
            "kind": "vROUTER"
        }

+ Response 200 (application/json)

        {
            "humanReadableName": "MyService",
            "id": 1,
            "created": "2016-05-05T23:06:33.835277Z",
            "updated": "2016-05-05T23:06:33.835302Z",
            "enacted": null,
            "policed": null,
            "backend_register": "{}",
            "backend_status": "0 - Provisioning in progress",
            "deleted": false,
            "write_protect": false,
            "lazy_blocked": false,
            "no_sync": false,
            "no_policy": false,
            "description": null,
            "enabled": true,
            "kind": "vROUTER",
            "name": "MyService",
            "versionNumber": null,
            "published": true,
            "view_url": "/admin/vrouter/vrouterservice/$id$/",
            "icon_url": null,
            "public_key": null,
            "private_key_fn": null,
            "service_specific_id": null,
            "service_specific_attribute": null
        }

### View a Service Detail [GET]

+ Parameters
    + id: 1 (number) - ID of the Service in the form of an integer

+ Response 200 (application/json)

        {
                "humanReadableName": "MyService",
                "id": 1,
                "created": "2016-05-05T23:06:33.835277Z",
                "updated": "2016-05-05T23:06:33.835302Z",
                "enacted": null,
                "policed": null,
                "backend_register": "{}",
                "backend_status": "0 - Provisioning in progress",
                "deleted": false,
                "write_protect": false,
                "lazy_blocked": false,
                "no_sync": false,
                "no_policy": false,
                "description": null,
                "enabled": true,
                "kind": "vROUTER",
                "name": "MyService",
                "versionNumber": null,
                "published": true,
                "view_url": "/admin/vrouter/vrouterservice/$id$/",
                "icon_url": null,
                "public_key": null,
                "private_key_fn": null,
                "service_specific_id": null,
                "service_specific_attribute": null
            }

### Delete a Service [DELETE]

+ Parameters
    + id: 1 (number) - ID of the Service in the form of an integer

+ Response 204
