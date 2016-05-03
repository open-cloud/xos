# Group Slices

List of the XOS slices

## Slices [/api/core/slices/{id}/]

### List all slices [GET]

+ Response 200 (application/json)

        [
            {
                "humanReadableName": "mysite_slice",
                "id": 1,
                "created": "2016-04-29T16:23:22.505072Z",
                "updated": "2016-04-29T16:23:22.504691Z",
                "enacted": null,
                "policed": "2016-04-29T16:23:22.781298Z",
                "backend_register": "{}",
                "backend_status": "0 - Provisioning in progress",
                "deleted": false,
                "write_protect": false,
                "lazy_blocked": false,
                "no_sync": false,
                "name": "mysite_slice",
                "enabled": true,
                "omf_friendly": false,
                "description": "",
                "slice_url": "",
                "site": "http://apt118.apt.emulab.net/api/core/sites/1/",
                "max_instances": 10,
                "service": null,
                "network": null,
                "exposed_ports": null,
                "serviceClass": "http://apt118.apt.emulab.net/api/core/serviceclasses/1/",
                "creator": "http://apt118.apt.emulab.net/api/core/users/1/",
                "default_flavor": null,
                "default_image": null,
                "mount_data_sets": "GenBank",
                "default_isolation": "vm",
                "networks": [
                    "http://apt118.apt.emulab.net/api/core/networks/1/"
                ]
            }
        ]
        