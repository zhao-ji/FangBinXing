#!/usr/bin/env python
# -*- coding: utf8 -*-

import select
import socket
import SocketServer
import struct

import logbook

import icmp


class ICMPServer(SocketServer.BaseServer):
    """Base class for various socket-based server classes.

    Defaults to synchronous IP stream (i.e., TCP).

    """

    address_family = socket.AF_INET

    socket_type = socket.SOCK_RAW

    protocol = socket.IPPROTO_ICMP

    request_queue_size = 5

    allow_reuse_address = False

    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
        """Constructor.  May be extended, do not override."""
        SocketServer.BaseServer.__init__(
            self, server_address, RequestHandlerClass)
        self.socket = socket.socket(self.address_family,
                                    self.socket_type,
                                    self.protocol,
                                    )
        if bind_and_activate:
            self.server_bind()
            # self.server_activate()

    def server_bind(self):
        """Called by constructor to bind the socket.

        May be overridden.

        """
        if self.allow_reuse_address:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)
        self.server_address = self.socket.getsockname()

    # def server_activate(self):
    #     """Called by constructor to activate the server.

    #     May be overridden.

    #     """
    #     self.socket.listen(self.request_queue_size)

    def fileno(self):
        """Return socket file number.

        Interface required by select().

        """
        return self.socket.fileno()



class ThreadedBaseServer(SocketServer.ThreadingMixIn, ICMPServer):
    pass


class ICMPRequestHandler(SocketServer.BaseRequestHandler):
    '''
    ICMP
    '''
    def handle(self):
        raw_addr = icmp.unpack(self.request.read(4096).strip())
        remote_addr = eval(raw_addr)
        logbook.info("get the remote addr {}".format(remote_addr))

        remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote.connect(remote_addr)
        logbook.info("connect the remote server")

        fdset = [self.request, remote]
        r, w, e = select.select(fdset, [], [])

        while True:
            if self.request in r:
                locate_data = self.request.recv(4096)
                logbook.info("locate: {}".format(repr(locate_data)))
                result = remote.send(locate_data)
                logbook.info("result: {}".format(result))
                if result <= 0:
                    logbook.info("breaking down")
                    break
            if remote in r:
                remote_data = remote.recv(4096)
                logbook.info("remote: {}".format(repr(remote_data)))
                result = self.request.send(remote_data)
                logbook.info("result: {}".format(result))
                if result <= 0:
                    logbook.info("breaking down")
                    break


def main():
    local_log = logbook.StderrHandler()
    local_log.format_string = (u'[{record.time:%H:%M:%S}] '
                               u'lineno:{record.lineno} '
                               u'{record.level_name}:{record.message}')
    local_log.push_application()

    logbook.info("start connecting...")
    server = ThreadedBaseServer(
        ('0.0.0.0', 233), ICMPRequestHandler,
        )
    logbook.info("start server at localhost in 233")
    server.serve_forever()


if __name__ == '__main__':
    main()
