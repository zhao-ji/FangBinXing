#! /usr/bin/env python
# -*- coding: utf8 -*-

from gevent import select
from gevent import socket
from gevent.server import StreamServer
import logbook


def handle(local, address):
    logbook.info("local address {}".format(address))

    remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote.connect(("chashuibiao.org", 233))
    logbook.info("connect the remote server")

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
