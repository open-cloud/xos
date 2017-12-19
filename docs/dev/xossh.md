# XOSSH

XOSSH is a cli tool that lets you perfom operations on the data model.
To set it up, connect to your `headnode` and execute:

```bash
bash /opt/cord/orchestration/xos/xos/tools/xossh
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