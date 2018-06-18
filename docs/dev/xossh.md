# XOSSH

XOSSH is a cli tool that lets you perfom operations on the data model.
To set it up, deploy the [`xossh`](../../charts/xossh.md) chart:

To connect to the `xossh` container, you can use this command (from the `helm-chart` folder):
```bash
bash xos-tools/xossh/xossh-attach.sh
```

It will connect to the `grpc` APIs exposed by `xos-core` and start a `python` shell.
Once started you should see this on your console:

```bash
__   __   ____     _____    _____   _    _
\ \ / /  / __ \   / ____|  / ____| | |  | |
 \ V /  | |  | | | (___   | (___   | |__| |
  > <   | |  | |  \___ \   \___ \  |  __  |
 / . \  | |__| |  ____) |  ____) | | |  | |
/_/ \_\  \____/  |_____/  |_____/  |_|  |_|

XOS Core server at xos-core.cord.lab:50051
Type "listObjects()" for a list of all objects
Type "listUtility()" for a list of utility functions
Type "login("username", "password")" to switch to a secure shell
Type "examples()" for some examples
xossh >>>
```
