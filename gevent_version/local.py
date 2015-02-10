#! /usr/bin/env python
# -*- coding: utf8 -*-

from gevent import socket
from gevent import spawn
from gevent.server import StreamServer
import logbook


def handle(local, address):
    logbook.info("local address {}".format(address))

    remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote.connect(("chashuibiao.org", 233))
    logbook.info("connect the remote server")

    logbook.info("OUT")
    spawn(process, local, remote)
    logbook.info("IN")
    spawn(process, remote, local)

def process(local, remote):
    local_data = local.recv(4096)
    logbook.info("local data: {}".format(repr(local_data)))
    result = remote.send(local_data)
    logbook.info("result: {}".format(result))


if __name__ == "__main__":
    server = StreamServer(("", 666), handle)
    logbook.info("start server at port: 666")
    server.serve_forever()
