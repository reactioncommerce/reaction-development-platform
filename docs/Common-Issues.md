# Common Issues

## port is already located

### Description

You are unable to start a service and see an error similar to:


> ERROR: for reactionusers_web_1  Cannot start service web: driver failed programming external connectivity on endpoint reactionusers_web_1
(0f45bf5f404e3ebe06f814a77324d4bd596110617105757d68754fb98834d8ed): Bind for
0.0.0.0:4000 failed: port is already allocated

The name of the service and the port number will vary.


### Fix

Another process is bound to the port specified in the error message. Stop the
service that's running on the port and start the service again.

## could not find an available address pool

### Description

* If you are using certain VPNs under linux, you may see the following error from docker
  * ` ERROR: could not find an available, non-overlapping IPv4 address pool among the defaults to assign to the network`

### Fix

To work around this, disconnect your VPN, then retry your make command

## connect: no route to host

### Description

You may encounter networking errors of several types when starting reaction services. Common causes of these issues include a host level firewall (such as `firewalld`) is blocking connections, the dependent services are not running, or inter-service links are misconfigured.

**Example**

The following error message was seen when firewalld prevented the hydra application server from connecting to the postgresql database server.

> time="2018-09-30T17:24:22Z" level=info msg="Unable to connect to database" error="Could not Connect to SQL: dial tcp 172.25.0.2:5432: connect: no route to host"

### Fix

Disable the firewall or configure specific rules to allow the connection. Confirm that services are running and that the values in use for inter-service URLs are correct.
