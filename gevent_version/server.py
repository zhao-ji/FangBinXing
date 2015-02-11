#! /usr/bin/env python
# -*- coding: utf8 -*-

from gevent import select
from gevent import socket
from gevent.server import StreamServer

import logbook


def handle(local, addr):
    logbook.info(addr)
    addr_raw = local.recv(1024).strip()
    addr = eval(addr_raw)
    remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote.connect(addr)
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
    server = StreamServer(("", 233), handle)
    logbook.info("start server at port: 233")
    server.serve_forever()
