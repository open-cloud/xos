## Sites [/api/core/sites/]

### List all sites [GET]

+ Response 200 (application/json)

        [
            {
                "humanReadableName": "mysite",
                "id": 1,
                "created": "2016-08-18T21:21:03.429133Z",
                "updated": "2016-08-18T21:21:06.676008Z",
                "enacted": null,
                "policed": null,
                "backend_register": "{}",
                "backend_status": "0 - Provisioning in progress",
                "deleted": false,
                "write_protect": false,
                "lazy_blocked": false,
                "no_sync": false,
                "no_policy": false,
                "name": "mysite",
                "site_url": "http://opencloud.us/",
                "enabled": true,
                "hosts_nodes": true,
                "hosts_users": true,
                "longitude": null,
                "latitude": null,
                "login_base": "mysite",
                "is_public": true,
                "abbreviated_name": "",
                "deployments": [
                    "1"
                ]
            }
        ]

## Sites [/api/core/sites/{id}/]

### View a Site Detail [GET]

+ Parameters
    + id: 1 (number) - ID of the Site in the form of an integer

+ Response 200 (application/json)
        
        {
            "humanReadableName": "mysite",
            "id": 1,
            "created": "2016-08-18T21:21:03.429133Z",
            "updated": "2016-08-18T21:21:06.676008Z",
            "enacted": null,
            "policed": null,
            "backend_register": "{}",
            "backend_status": "0 - Provisioning in progress",
            "deleted": false,
            "write_protect": false,
            "lazy_blocked": false,
            "no_sync": false,
            "no_policy": false,
            "name": "mysite",
            "site_url": "http://opencloud.us/",
            "enabled": true,
            "hosts_nodes": true,
            "hosts_users": true,
            "longitude": null,
            "latitude": null,
            "login_base": "mysite",
            "is_public": true,
            "abbreviated_name": "",
            "deployments": [
                "1"
            ]
        }
