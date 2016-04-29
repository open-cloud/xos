# Group Users

List of the XOS users

## Users [/api/core/users/{id}/]

### List all Users [GET]

+ Response 200 (application/json)

        [
            {
                "id": 2,
                "password": "pbkdf2_sha256$12000$9gn8DmZuIoz2$YPQkx3AOOV7jZNYr2ddrgUCkiuaPpvb8+aJR7RwLZNA=",
                "last_login": "2016-04-12T18:50:45.880823Z",
                "email": "johndoe@myhouse.com",
                "username": "johndoe@myhouse.com",
                "firstname": "john",
                "lastname": "doe",
                "phone": null,
                "user_url": null,
                "site": "http://xos.dev:9999/api/core/sites/1/",
                "public_key": null,
                "is_active": true,
                "is_admin": false,
                "is_staff": true,
                "is_readonly": false,
                "is_registering": false,
                "is_appuser": false,
                "login_page": null,
                "created": "2016-04-12T18:50:45.912602Z",
                "updated": "2016-04-12T18:50:45.912671Z",
                "enacted": null,
                "policed": null,
                "backend_status": "Provisioning in progress",
                "deleted": false,
                "write_protect": false,
                "timezone": "America/New_York"
            }
        ]
        