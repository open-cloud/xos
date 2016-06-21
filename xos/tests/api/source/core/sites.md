# Group Sites

List of the XOS sites

## Sites [/api/core/sites/{id}/]

### List all sites [GET]

+ Response 200 (application/json)

        {
            "humanReadableName": "mysite",
            "id": 1,
            "created": "2016-04-29T16:19:03.587770Z",
            "updated": "2016-04-29T16:19:05.651933Z",
            "enacted": null,
            "policed": null,
            "backend_register": "{}",
            "backend_status": "0 - Provisioning in progress",
            "deleted": false,
            "write_protect": false,
            "lazy_blocked": false,
            "no_sync": false,
            "name": "MySite",
            "site_url": "http://opencord.us/",
            "enabled": true,
            "hosts_nodes": true,
            "hosts_users": true,
            "location": null,
            "longitude": null,
            "latitude": null,
            "login_base": "mysite",
            "is_public": true,
            "abbreviated_name": "",
            "deployments": [
                "1"
            ]
        }