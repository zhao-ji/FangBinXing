#! /usr/bin/env python
# -*- coding: utf8 -*-

import select
import socket
import SocketServer

import logbook


class RemoteSocketServer(SocketServer.StreamRequestHandler):
    '''
    tcp
    '''
    def handle(self):
        remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote.connect(("0.0.0.0", 233))
        logbook.info("connect the remote server")

        while True:
            fdset = [self.connection, remote]
            r, w, e = select.select(fdset, [], [])
            if self.connection in r:
                locate_data = self.connection.recv(4096)
                logbook.info("locate: {}".format(repr(locate_data)))
                result = remote.send(locate_data)
                logbook.info("result: {}".format(result))
                if result <= 0:
                    logbook.info("breaking down")
                    break
            if remote in r:
                remote_data = remote.recv(4096)
                logbook.info("remote: {}".format(repr(remote_data)))
                result = self.connection.send(remote_data)
                logbook.info("result: {}".format(result))
                if result <= 0:
                    logbook.info("breaking down")
                    break


if __name__ == "__main__":
    server = SocketServer.ThreadingTCPServer(
        ("", 666), RemoteSocketServer,
        )
    logbook.info("start server at port: 666")
    server.serve_forever()
