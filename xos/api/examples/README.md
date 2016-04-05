## XOS REST API Examples

This directory contains examples that demonstrate using the XOS REST API using the `curl` command-line tool.

To get started, edit `config.sh` so that it points to a valid XOS server.

We recommend running the following examples in order:

 * `add_subscriber.sh` ... add a cord subscriber using account number 1238
 * `update_subscriber.sh` ... update the subscriber's upstream_bandwidth feature
 * `add_volt_to_subscriber.sh` ... add a vOLT to the subscriber with s-tag 33 and c-tag 133
 * `get_subscriber.sh` ... get an entire subscriber object
 * `get_subscriber_features.sh` ... get the features of a subscriber
 * `delete_volt_from_subscriber.sh` ... remove the vOLT from the subscriber
 * `delete_subscriber.sh` ... delete the subscriber that has account number 1238
