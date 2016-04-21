# Group Subscribers

Resource related to the CORD Subscribers.

## Subscribers [/api/tenant/cord/subscriber/{subscriber_id}/]

### List All Subscribers [GET]

+ Response 200 (application/json)

        [
            {
                "humanReadableName": "cordSubscriber-1",
                "id": 1,
                "features": {
                    "cdn": false,
                    "uplink_speed": 1000000000,
                    "downlink_speed": 1000000000,
                    "uverse": false,
                    "status": "enabled"
                },
                "identity": {
                    "account_num": "123",
                    "name": "My House"
                },
                "related": {
                    "instance_name": "mysite_vcpe",
                    "vsg_id": 4,
                    "compute_node_name": "node2.opencloud.us",
                    "c_tag": "432",
                    "instance_id": 1,
                    "wan_container_ip": null,
                    "volt_id": 3,
                    "s_tag": "222"
                }
            }
        ]


### View a Subscriber Detail [GET]

+ Parameters
    + subscriber_id: 1 (number) - ID of the Subscriber in the form of an integer

+ Response 200 (application/json)
 
        {
            "humanReadableName": "cordSubscriber-1", 
            "id": 1, 
            "features": { 
                "cdn": false, 
                "uplink_speed": 1000000000, 
                "downlink_speed": 1000000000, 
                "uverse": false, 
                "status": "enabled" 
            }, 
            "identity": { 
                "account_num": "123",
                "name": "My House"
            }, 
            "related": { 
                "instance_name": "mysite_vcpe", 
                "vsg_id": 4, 
                "compute_node_name": "node2.opencloud.us",
                "c_tag": "432", 
                "instance_id": 1, 
                "wan_container_ip": null, 
                "volt_id": 3, 
                "s_tag": "222" 
            } 
        }

### Delete a Subscriber [DELETE]

+ Parameters
    + subscriber_id: 1 (number) - ID of the Subscriber in the form of an integer

+ Response 204

### Subscriber features [/api/tenant/cord/subscriber/{subscriber_id}/features/]

+ Parameters
    + subscriber_id: 1 (number) - ID of the Subscriber in the form of an integer

### View a Subscriber Features Detail [GET]

+ Response 200 (application/json)

        {
            "cdn": false, 
            "uplink_speed": 1000000000, 
            "downlink_speed": 1000000000, 
            "uverse": true, 
            "status": "enabled"
        }

#### Subscriber features uplink_speed [/api/tenant/cord/subscriber/{subscriber_id}/features/uplink_speed/]

+ Parameters
    + subscriber_id: 1 (number) - ID of the Subscriber in the form of an integer

#### Read Subscriber uplink_speed [GET]

+ Response 200 (application/json)

        {
            "uplink_speed": 1000000000
        }

#### Update Subscriber uplink_speed [PUT]

+ Request 200 (application/json)

        {
            "uplink_speed": 1000000000
        }

+ Response 200 (application/json)

        {
            "uplink_speed": 1000000000
        }

#### Subscriber features downlink_speed [/api/tenant/cord/subscriber/{subscriber_id}/features/downlink_speed/]

+ Parameters
    + subscriber_id: 1 (number) - ID of the Subscriber in the form of an integer

#### Read Subscriber downlink_speed [GET]

+ Response 200 (application/json)

        {
            "downlink_speed": 1000000000
        }

#### Update Subscriber downlink_speed [PUT]

+ Request 200 (application/json)

        {
            "downlink_speed": 1000000000
        }

+ Response 200 (application/json)

        {
            "downlink_speed": 1000000000
        }

#### Subscriber features cdn [/api/tenant/cord/subscriber/{subscriber_id}/features/cdn/]

+ Parameters
    + subscriber_id: 1 (number) - ID of the Subscriber in the form of an integer

#### Read Subscriber cdn [GET]

+ Response 200 (application/json)

        {
            "cdn": false
        }

#### Update Subscriber cdn [PUT]

+ Request 200 (application/json)

        {
            "cdn": false
        }

+ Response 200 (application/json)

        {
            "cdn": false
        }

#### Subscriber features uverse [/api/tenant/cord/subscriber/{subscriber_id}/features/uverse/]

+ Parameters
    + subscriber_id: 1 (number) - ID of the Subscriber in the form of an integer

#### Read Subscriber uverse [GET]

+ Response 200 (application/json)

        {
            "uverse": false
        }

#### Update Subscriber uverse [PUT]

+ Request 200 (application/json)

        {
            "uverse": false
        }

+ Response 200 (application/json)

        {
            "uverse": false
        }

#### Subscriber features status [/api/tenant/cord/subscriber/{subscriber_id}/features/status/]

+ Parameters
    + subscriber_id: 1 (number) - ID of the Subscriber in the form of an integer

#### Read Subscriber status [GET]

+ Response 200 (application/json)

        {
            "status": "enabled"
        }

#### Update Subscriber status [PUT]

+ Request 200 (application/json)

        {
            "status": "enabled"
        }

+ Response 200 (application/json)

        {
            "status": "enabled"
        }