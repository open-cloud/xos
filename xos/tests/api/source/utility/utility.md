## Login [/api/utility/login/]

### Log a user in the system [POST]

+ Request (application/json)

        {
            "username": "padmin@vicci.org",
            "password": "letmein"
        }

+ Response 200 (application/json)

        {
            "xoscsrftoken":"xuvsRC1jkXAsnrdRlgJvcXpmtthTAqqf",
            "xossessionid":"7ds5a3wzjlgbjqo4odkd25qsm0j2s6zg",
            "user": "{\"policed\": null, \"site\": 3, \"is_appuser\": false, \"is_staff\": true, \"backend_status\": \"Provisioning in progress\", \"id\": 3, \"is_registering\": false, \"last_login\": \"2016-04-30T22:51:04.788675+00:00\", \"email\": \"padmin@vicci.org\", \"no_sync\": false, \"username\": \"padmin@vicci.org\", \"dashboards\": [11], \"login_page\": null, \"firstname\": \"XOS\", \"user_url\": null, \"deleted\": false, \"lastname\": \"admin\", \"is_active\": true, \"lazy_blocked\": false, \"phone\": null, \"is_admin\": true, \"enacted\": null, \"public_key\": null, \"is_readonly\": false, \"no_policy\": false, \"write_protect\": false}"
        }

## Logout [/api/utility/logout/]

### Log a user out of the system [POST]

+ Request (application/json)

        {
            "xossessionid": "sessionId"
        }

+ Response 200 (application/json)

## Port Forwarding [/api/utility/portforwarding/]

Contains the set of port forwarding mappings for each compute node.
Used on OpenCloud to setup port forwarding for nat-net.

### List port forwarding objects [GET]

+ Response 200 (application/json)

        [
            {
                "id": 79,
                "ip": "172.16.0.36",
                "ports": "tcp 2222, tcp 25566",
                "hostname": "node1.opencloud.us"
            },
            {
                "id": 131,
                "ip": "172.16.0.16",
                "ports": "udp 53, tcp 8017",
                "hostname": "node2.opencloud.us"
            }
        ]

## Slices Plus [/api/utility/slicesplus/]

A list of slices with addictional information, it is used in the Tenant custom dashboard.

### List Slices objects [GET]

+ Response 200 (application/json)

        [
             {
                "humanReadableName": "mysite_management",
                "id": 2,
                "created": "2016-06-29T18:43:50.730912Z",
                "updated": "2016-06-29T18:43:50.730789Z",
                "enacted": null,
                "name": "mysite_management",
                "enabled": true,
                "omf_friendly": false,
                "description": "",
                "slice_url": "",
                "site": 2,
                "max_instances": 10,
                "service": null,
                "network": "noauto",
                "mount_data_sets": "GenBank",
                "default_image": null,
                "default_flavor": null,
                "serviceClass": null,
                "creator": 2,
                "networks": [],
                "network_ports": "",
                "backendIcon": "/static/admin/img/icon_clock.gif",
                "backendHtml": "<span title=\"Pending sync, last_status = 0 - Provisioning in progress\"><img src=\"/static/admin/img/icon_clock.gif\"></span>",
                "current_user_roles": [],
                "instance_distribution": {},
                "instance_distribution_ready": {},
                "instance_total": 0,
                "instance_total_ready": 0,
                "instance_status": {},
                "users": [],
                "user_names": [],
                "current_user_can_see": true
            }
        ]

## Synchronizer [/api/utility/synchronizer/]

Lists the Diag objects for synchronizers. From here you can get the synchronizer status.

### List Diag objects [GET]

+ Response 200 (application/json)

        [
            {
                "id": 3,
                "name": "onboarding",
                "backend_status": "1 - Bottom Of Loop",
                "backend_register": "{\"last_duration\": 0.18996095657348633, \"last_run\": 1467923907.908469}"
            }
        ]

## Onboarding [/api/utility/onboarding/{service}/ready]

Used to get the status of onboarding, to determine if services have been to successfully onboarded and if the XOS UI container has been built.

### Get service status [GET]

+ Parameters
    + service: services/vsg (string) - Name of the service to wait for


+ Response 200 (text/plain)

        true

## Tosca [/api/utility/tosca/run/]

### Load a Tosca recipe [POST]

+ Request (application/json)

        {
            "recipe": "tosca_definitions_version: tosca_simple_yaml_1_0\n\ndescription: Onboard the exampleservice\n\nimports:\n   - custom_types/xos.yaml\n\ntopology_template:\n  node_templates:\n    test_site:\n      type: tosca.nodes.Site\n      properties:\n          display_name: Test Site\n          site_url: https://www.onlab.us/"
        }

+ Response 200 (application/json)

        {
            "log_msgs":[
                "ordered_names: ['test_site']",
                "Created Site 'Test Site'"
            ]
        }

## Ssh Keys [/api/utility/sshkeys/]

Returns the set of ssh keys for instances. Used on OpenCloud to configure ssh-proxy to instances.

### List ssh keys by instance [GET]

+ Response 200 (application/json)

        [
            {
                "id": "instance-00000001",
                "public_keys": [
                    "ssh-rsa xxyyzz\r\n"
                ],
                "node_name": "node1.opencloud.us"
            },
            {
                "id": "instance-00000001",
                "public_keys": [
                    "ssh-rsa xxyyzz\r\n"
                ],
                "node_name": "node2.opencloud.us"
            }
        ]