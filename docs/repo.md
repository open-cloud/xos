# Download Source Code

The easiest way to download source code for XOS—including the
XOS core, the XOS-related interfaces (e.g., GUI, TOSCA), the helm
charts used to deploy XOS, and the model/synchronizers
for the services being managed by XOS—is to use the `repo` tool.

## Install repo

If you don't already have `repo` installed, you may be able to install
it with your system package manager, or you can follow these
[instructions from the android source site](https://source.android.com/source/downloading#installing-repo):

```sh
curl -o /tmp/repo 'https://gerrit.opencord.org/gitweb?p=repo.git;a=blob_plain;f=repo;hb=refs/heads/stable'
echo '394d93ac7261d59db58afa49bb5f88386fea8518792491ee3db8baab49c3ecda  /tmp/repo' | sha256sum -c -
sudo mv /tmp/repo /usr/local/bin/repo
sudo chmod a+x /usr/local/bin/repo
```

> **Note:** You may want to install `repo` using the official
> repository instead. We forked the original repository and host a copy of the
> file to make repo downloadable also by organizations that don't have access
> to Google servers.

## Download Repositories

We assume the XOS repositories are checked out into directory `$SRC_DIR`:

```shell
mkdir $SRC_DIR/
cd $SRC_DIR
repo init -u https://gerrit.opencord.org/xos-manifest -b master
repo sync
```

## Development Notes

You can also use `repo` to download the latest patchsets from Gerrit, and
to contribute code back into Gerrit (for review). More information on how
to do both are available on the [CORD Wiki](https://wiki.opencord.org/display/CORD/Working+with+Gerrit).
