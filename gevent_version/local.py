#! /usr/bin/env python
# -*- coding: utf8 -*-

from gevent import select
from gevent import socket
from gevent.server import StreamServer

import logbook

REMOTE_ADDR = ("chashuibiao.org", 233)

def handle(local, address):
    # 1. Authorization
    self.request.recv(262)
    self.request.send(b"\x05\x00")

    # 2. Request
    data = self.rfile.read(4)
    mode = ord(data[1])
    if mode != 1: # if not a TCP/IP stream connection
        reply = b"\x05\x07\x00\x01"  # Command not supported
        self.request.send(reply)
        return

    addrtype = ord(data[3])
    if addrtype == 1:       # IPv4
        # 4 bytes for IPv4 address
        addr = socket.inet_ntoa(self.rfile.read(4))
        logbook.info("ipv4 address: {}".format(addr))
    elif addrtype == 3:     # Domain name
        # 1 byte of name length followed by the name for Domain name
        addr = self.rfile.read(ord(self.rfile.read(1)[0]))
        logbook.info("domain name is {}".format(addr))

    # port number in a network byte order, 2 bytes
    port = struct.unpack('>H', self.rfile.read(2))[0]
    logbook.info("request port is {}".format(port))

    # 3. Response
    reply_prefix = b"\x05\x00\x00\x01"
    reply_suffix = b"{}{}".format(
        socket.inet_aton("0.0.0.0"),
        struct.pack(">H", 65535),
        )
    reply = b"{}{}".format(reply_prefix, reply_suffix)
    self.request.send(reply)

    # 4. Connect
    remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote.connect(REMOTE_ADDR)
    logbook.info("connect the remote server")

    # 5. Communicate
    goal_addr = (addr, port)
    remote.send(repr(goal_addr))
    process(local, remote)

def process(local, remote):
    fdset = [local, remote]
    while True:
        r, w, e = select.select(fdset, [], [])
        if local in r:
            if remote.send(local.recv(4096)) <= 0:
                logbook.info("local breaking down")
                break
        if remote in r:
            if local.send(remote.recv(4096)) <= 0:
                logbook.info("remote breaking down")
                break


if __name__ == "__main__":
    server = StreamServer(("", 666), handle)
    logbook.info("start server at port: 666")
    server.serve_forever()
