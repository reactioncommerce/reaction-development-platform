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
