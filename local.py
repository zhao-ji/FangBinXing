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
        self.data = self.request.recv(4096).strip()
        remote_address, remote_port = self.data.split(":")
        logbook.info("address: {}, port: {}".format(
                     remote_address, remote_port))

        remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote.connect((remote_address, int(remote_port)))
        self.process(self.request, remote)


    def process(self, locate, remote):
        fdset = [locate, remote]
        while True:
            r, w, e = select.select(fdset, [], [])
            if locate in r:
                locate_data = locate.recv(4096)
                logbook.info("locate: {}".format(locate_data))
                result = remote.send(locate_data)
                logbook.info("result: {}".format(result))
                if result <= 0:
                    logbook.info("breaking down")
                    break
            if remote in r:
                remote_data = remote.recv(4096)
                logbook.info("remote: {}".format(remote_data))
                result = locate.send(remote_data)
                logbook.info("result: {}".format(result))
                if result <= 0:
                    logbook.info("breaking down")
                    break


if __name__ == "__main__":
    server = SocketServer.ThreadingTCPServer(
        ("", 233), RemoteSocketServer,
        )
    logbook.info("start server at port: 233")
    server.serve_forever()
