# Group vOLT

OLT devices aggregate a set of subscriber connections

## vOLT Collection [/api/tenant/cord/volt/{volt_id}/]

### List all vOLT [GET]

+ Response 200 (application/json)

        [
            {
                "humanReadableName": "vOLT-tenant-1",
                "id": 1,
                "service_specific_id": "123",
                "s_tag": "222",
                "c_tag": "432",
                "subscriber": 1,
                "related": {
                    "instance_id": 1,
                    "instance_name": "mysite_vcpe",
                    "vsg_id": 4,
                    "wan_container_ip": null,
                    "compute_node_name": "node2.opencloud.us"
                }
            }
        ]

### Create a vOLT [POST]

+ Request (application/json)

        {
            "s_tag": "222",
            "c_tag": "432",
            "subscriber": 1
        }

+ Response 201 (application/json)

        {
                "humanReadableName": "vOLT-tenant-1",
                "id": 1,
                "service_specific_id": "123",
                "s_tag": "222",
                "c_tag": "432",
                "subscriber": 1,
                "related": {
                    "instance_id": 1,
                    "instance_name": "mysite_vcpe",
                    "vsg_id": 4,
                    "wan_container_ip": null,
                    "compute_node_name": "node2.opencloud.us"
                }
            }

### View a vOLT Detail [GET]

+ Parameters
    + volt_id: 1 (number) - ID of the vOLT in the form of an integer

+ Response 200 (application/json)

        {
            "humanReadableName": "vOLT-tenant-1",
            "id": 1,
            "service_specific_id": "123",
            "s_tag": "222",
            "c_tag": "432",
            "subscriber": 1,
            "related": {
                "instance_id": 1,
                "instance_name": "mysite_vcpe",
                "vsg_id": 4,
                "wan_container_ip": null,
                "compute_node_name": "node2.opencloud.us"
            }
        }
