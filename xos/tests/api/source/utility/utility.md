# Group Utility

List of the XOS Utility API

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
            "user": {
                "policed": null,
                "site": 1,
                "is_appuser": false,
                "is_staff": true,
                "backend_status": "Provisioning in progress",
                "id": 1,
                "is_registering": false,
                "last_login": "2016-04-29T20:35:58.979122+00:00",
                "email": "padmin@vicci.org",
                "no_sync": false,
                "username": "padmin@vicci.org",
                "dashboards": [
                    4,
                    3,
                    5
                ],
                "login_page": null,
                "firstname": "XOS",
                "user_url": null,
                "deleted": false,
                "lastname": "admin",
                "is_active": true,
                "lazy_blocked": false,
                "phone": null,
                "is_admin": true,
                "enacted": null,
                "public_key": null,
                "is_readonly": false,
                "no_policy": false,
                "write_protect": false
            }
        }

## Logout [/api/utility/logout/]

### Log a user out of the system [POST]

+ Request (application/json)
        {xossessionid: "sessionId"}

+ Response 200 (application/json)
