# Backup/Restore

XOS holds authoritative state for many components in a deployment. This typically includes configuration of services such as ONOS and VOLTHA as well as operational data such as subscriber state. Even the user accounts that secure access to the XOS API are part of the data model. This page documents the requirements, design, and implementation of the XOS backup / restore feature.

XOS shares many similarities with a traditional database system, but XOS also provides unique capabilities and challenges that a traditional database system may not have. For example, while XOS maintains a database schema and stores data within that schema, XOS is also designed to be extensible in ways that a traditional database may not be. Services augment XOS, with not only schema but also custom logic. XOS acts as a coordinator for these services and enforces rules (such as versioning and dependency enforcement) on service behavior. Any backup solution for XOS must encompass not only the traditional database aspects, but also address contributions that are unique to XOS.

Fault Tolerance and Backup are two different goals. Fault Tolerance ensures that a component remains operational in the case of failure. Backup and Restore are concerned with storing state at a specific time and returning the system to that state on demand. Backup may be useful, for example, when performing high-risk operations on a pod such as upgrading software. An operator may create a backup and save it as a "last known good" state, knowing that he/she can easily return to that state should an upgrade fail.


Performance metrics and logging are outside the scope of this page, as these are typically handled by other systems (Prometheus and ElkStack, respectively).

## Design Requirements

The primary requirement is to implement a unified API that allows operators to issue backup and restore operations on a deployed pod. This API has the following requirements:

1. The API exposes the following capabilities:
    * Initiation of Backup/restore operations
    * Confirmation of whether backup/restore operations were completed successfully
    * Retrieve backup files from the system
    * Supply restore files to the system
    * List available backup files
2. The API is protected with security features that prevent unauthorized persons from initiating a backup or restore, or retrieving the contents of any previously-performed backup.
3. Backups should have self-verification features, for example checksums/hashes, etc. It should be possible by examining a backup to ensure that the backup has a high-probability of being restored successfully.
4. There must be an interlock present to prevent the database from changing while a backup or restore is in progress.
5. The system should be able to recover from a failed restore operation, preserving the state before the restore was attempted.
6. Backup should encompass all necessary state to yield a functional xos-core upon restore. Any artifacts that XOS synchronizers create in the core must either be backed up and restored, or re-created automatically during core restart.

## Design Considerations

### Alternative #1: External, Database-centric

As XOS is backed by a traditional database system, in our case Postgres, one design alternative is to address backup and restore within the context of this database rather than involving XOS directly in the process. For example, a script could initiate the necessary Kubernetes or Helm commands to pause XOS and to initiate a postgres dump into a shared volume, or a local disk on one of the Kubernetes nodes, or some other location accessible to Kubernetes. The process is roughly as follows:

1. Signal XOS to enter a "stopped" state where XOS ceases responding to requests
2. Wait for XOS to confirm this stopped state has been reached.
3. Backup/Restore database by performing operations directly on the database container.
4. Signal XOS to start
5. Wait for XOS to confirm that the start state has been reached.

The advantage of this approach is that it is relatively straightforward to implement, using existing tools (Kubernetes, Helm, Postgres). As XOS is not directly involved, this approach does not add complexity to the XOS implementation directly, but may instead push that complexity into externally implementing an interlock to prevent XOS and its synchronizers from running while the backup is in progress, and a probing mechanism to ensure that XOS has successfully restarted after a restore.

The disadvantage of this approach is that using a set of separate and independent tools implies a set of separate and independent APIs and custom scripts are required to sequence a backup or restore operation. It also ties the backup and restore operations to specific tools and file formats, in this case Postgres, rather than providing an abstraction that hides the implementation. Different tools may have different security features. As such, to meet the unified API requirement would require writing a new component to implement the backup/restore API, provide a security abstraction, and interlock with XOS. This new component would to some extent duplicate the functionality of XOS.

### Alternative #2: Internal, XOS-centric

In this approach, the backup and restore feature is built directly into XOS. The process is roughly as follows:

1. Using the XOS API, the operator instructs XOS to begin a backup or restore operation.
2. XOS pauses processing or requests.
3. Backup/restore is performed by XOS.
4. Indication of backup/restore completion state is recorded in the XOS data model.
5. XOS resumes processing or requests.

The advantage of this approach is that providing a unified API to a set of disaggregated components is one of the purposes that XOS was designed to serve. XOS already provides a security abstraction for its API. XOS already has logic for performing In Service Software Update (ISSU) that has some overlapping requirements and functionality with the backup/restore feature. There's no need to implement an external interlock with XOS to ensure the database is not modified during backup, as XOS is capable of implementing that interlock internally.

The disadvantage of this approach is that it places a high burden of correctness and robustness on XOS, as a critical failure during restore that left XOS unable to process requests would prevent the operator from initiating any further restore requests. XOS must be written to check for failures during the restore process and rollback as necessary and to guarantee the core is always brought back up in an operational state.

### Design decision

It was decided that the ability of XOS to implement any interlock and consistency check internally and to use XOS's existing API were sufficient to warrant choosing alternative #2. In addition, being able to leverage the backup/restore feature during ISSU was seen as a considerable advantage. Alternative #2 was chosen and implemented.

> Note: This does not necessarily preclude also implementing an external backup/restore feature using alternative #1. An operator may still interact with components directly through Kubernetes or Helm. Operators may have in-house tools for interacting with Kubernetes deployments. These tools could be used instead of, or in addition to, the backup and restore feature that is built directly into XOS.

## Implementation

This section documents the backup and restore feature implementation.

### Backup and Restore requests

Backup and Restore operations are initiated by creating objects in the XOS data model, just like any other operation. There are two related data model objects:

* `BackupFile`: Represents a file that can be used as the target of a Backup operation or the source of a Restore operation.
    * `name`: A human readable name for the file.
    * `uri`: URI where the file resides on the server, typically a `file:///` URI.
    * `checksum`: Checksum of the file, in the format `<algorighm>:<hash>`
    * `status`: Either `retreived`, `sent`, or `inprogress`.
    * `backend_filename`: An internal field used by the backup/restore feature to point to where the file exists locally. Not intended for external use.
* `BackupOperation`: Represents a backup operation that should be performed by XOS. Contains both the request from the operator and the response from XOS to that request.
    * `file`: ForeignKey that points to a BackupFile where the backup should be made to, or the restore made from. The `file` field is mandatory for `restore` operations, but it is optional for `create` operations. If no file is specified for a `create`, then XOS will generate a file automatically.
    * `component`: The component that should be backed up. `xos` is currently the only permitted value, but this field is provided to permit the modeling to be extensible to backing up other components in the future.
    * `operation`: This field is `create` to create a backup, `restore` to restore a previously created backup, or `verify` to verify a previously created backup.
    * `status`: This field holds the result of an operation and is set to one of `created`, `restored`, `failed`, `inprogress`, or `orphaned`. Because the result of a `create` operation is not known until after the backup has been created, if that backup is subsequently the source of a `restore` operation, then value of `status` will for the `create` operation will be lost. The `orphaned` status accounts for that special case.
    * `error_msg`: In the case of a `failed` status, this field holds an error message.
    * `effective_date`: This is a date and time the backup was created or restored.
    * `uuid`: A unique identifier is generated for each request, that may be used by clients who are polling for status to determine when a specific operation completed.

After creating an operation, the client should poll until the operation's status field indicates that the operation is complete. A create operation generally follows this procedure:

```pseudocode
request = CreateBackupOperation(file=None, operation="create", component="xos")
while true:
    result = FilterBackupOperation(uuid = request.uuid)
    if len(result) > 0  and result[0].enacted > result[0].updated :
        # We found the operation and it has been enacted
        break
file = GetBackupFile(id = result[0].file)
download_file_contents(file.uri, local_filename)
```

A restore operation is similar, but must specify a BackupFile:

```pseudocode
upload_file_contents(local_filename, remote_uri)
file = CreateBackupFile(name="somename", uri=remote_uri)
request = CreateBackupOperation(file=file, operation="restore", component="xos")
while true:
    result = FilterBackupOperation(uuid = request.uuid)
    if len(result) > 0  and result[0].enacted > result[0].updated :
        # We found the operation and it has been enacted
        break
```

### The xos-core main loop

The XOS core container implements a continuous loop that alternates between serving the XOS API and performing system maintenance tasks such as backup and restore. Conceptually,

```pseudocode
while true do
    Perform Maintenance
        Run Migrations
        Rebuild Protobufs
        Execute Backup Operations
    Serve API
        Contunously process gRPC requests until maintenance tasks are required
```

This serves as the primary interlock between maintenance tasks and API service. A natural consequence is that the API is unavailable whenever maintenance tasks are being performed. Exactly what causes the API Server to exit and run maintenance depends on the specific type of maintenance to be performed. For example, issuing an API call to onboard a new service requires database migration maintenance be performed, whereas submitting a backup or restore request causes backup/restore maintenance to be performed.

> Note: It's possible in the future a more sophisticated main loop may be implemented. For example, it might be advantageous to leave the API server in a "read-only" mode rather than exiting entirely. Such improvements are deferred to future work.

### Handling incoming BackupOperations

The `Serve API` and `Execute Backup Operations` tasks of the xos-core main loop are implemented in two independent python processes. There are two directories used for coordination between the `Serve API` task and the `Execute Backup Operations` maintenance task. These are the `request` directory and the `response` directory. Communicating using files in these request and response directories is a way to decouple the parts of XOS that directly use the data model (and require a fully functional and consistent data model) from the parts of XOS that maintain the data model.

During the `Serve API` portion of the core main loop, a thread named `BackupSetWatcher` polls the database for changes. Any time a new BackupOperation is detected, this thread will write the request to a file in the request directory and cause `Serve API` to exit. The main loop will then undergo another iteration, invoking maintenance tasks at the top of the loop.

The `Execute Backup Operations` maintenance task looks for any pending request files in the request directory, If a request is found then it will execute that request and write the result to a file in the response directory. Only one request is permitted at a time. If multiple requests are present then only the first one will be acted on.

After the maintenance tasks are complete, when the `Serve API` phase begins again, the first thing the xos-core does is to look for any responses in the response directory and update them in the data model with the `status` and other relevant feedback fields populated.



