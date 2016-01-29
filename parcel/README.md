## Synopsis

A high performance HTTP download client that leverages the speed of UDP without sacrificing reliability.

Parcel is written on top of the UDT protocol and bound to a python interface.  Parcel's software is comprised of a *parcel-server* and a *parcel* client.

## Download and run


## Installing from source

You can also install from source with:
```
❯ pip install -e 'git+https://github.com/LabAdvComp/parcel#egg=parcel'
```

## Usage

## Proxy your app traffic over UDT!

The idea of the proxy is to tunnel traffic from one LAN to another remote LAN via UDT.  You can use this to connect any client to a remote server over a WAN via UDT. 

**Example**

You have the following:

- Host 1: This is the host with your custom client running on it.  You want to listen for incoming local TCP connections on this host and translate them to send remotely over UDT.  You should run the `parcel-tcp2udt` proxy on Host 1. This is represented by LAN 1 in the diagram below.
- Host 2: This is the host with your custom server running on it.  You want to listen for incoming UDT connections on this host and translate them to local TCP.  You should run the `parcel-udt2tcp` proxy on Host 1. This is represented by LAN 2 in the diagram below.
- You have a client running on `host1` (LAN 1)
- You have a server running on `host2` (LAN 2) on port `port`

1. Run `parcel-tcp2udt host2:9000` 
     - This will start a proxy that will connect to the `udt2tcp` proxy which is by default bound to port `9000`.
2. Run `parcel-udt2tcp localhost:port`
     - This will start a proxy on `host2`, port `9000` that will listen for incoming UDT connections, translate them to TCP, and send them along to your server on `host2:port`


<p align="center">
  <img src="https://raw.githubusercontent.com/LabAdvComp/parcel/develop/resources/proxy.png" alt="Proxy diagram"/>
</p>

- In the diagram above, the arrows relate to the direction of the socket connection, not the traffic.  The information transfer is actually bidirectional, i.e. both proxies can send and receive data.  
- This is a drop in replacement for the workflow where the client connects directly to the server over the WAN.
- Your client connects to the `tcp2udt` proxy which connects to the `udt2tcp` proxy which connects to your server.  Then information flows back and forth until either the client or server breaks the connection.
- The proxies can support multiple connections at once in parallel.

## HTTP Download

#### Using: TCP

This is the default option and can be run directly against a REST api without any additional server. Using this method, you are likely to see decreased performance over high latency networks.

#### Using: UDT

The client can be run in conjunction with a parcel server, or without one.  The advantage of running the client with the server (option `udt`) is the UDT proxy layer.  This prevents performance degredation of Wide Area Networks.

The server is given a REST endpoint with access to data.  The client connects to the server via UDT and the data is translated to a local TCP connection. Any TCP response is then proxied back using UDT.

Note: The UDT option is not currently bundled with executable binaries, you must install from source.

## Example Usage
To use the client interactively
```
❯ parcel
```
OR
```
❯ parcel -t token_file file_id1 file_id2
```
OR
```
❯ parcel -u -t token_file file_id1 file_id2
```

## Motivation

TCP is the most widely used reliable network transport protocol. However, over high performance, wide area networks, TCP has been show to reach a bottleneck before UDP.

UDT (UDP Based Data transfer) is a reliable application level protocol for transferring bulk data over wide area networks.

## Dependencies

- [Python 2.7+](http://python.org/)
- [Python pip](https://pypi.python.org/pypi/pip)

## Tests

To run the tests:

```
❯ pip install pytest
❯ py.test
```
