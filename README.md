# dsws-client

Python wrapper for the Datastream Web Services API (DSWS)

To Connect to the Refinitiv Datastream database via Datastream Web Services, you need to have a Datastream subscription and a username/password to use this package.

Please note that this is an unofficial client not affiliated with Refinitiv.

This package includes all functionalities required to get data from DSWS.

## Why?

There are two client libraries for DSWS that I am aware of, the official [DatastreamDSWS][1] and [pydatastream][2]. Both of them return data only as pandas dataframes. I needed something that doesn't depend on pandas, so I decided to make this client.

[1]: https://github.com/DatastreamDSWS/Datastream
[2]: https://github.com/vfilimonov/pydatastream
