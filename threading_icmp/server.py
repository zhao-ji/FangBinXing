#!/usr/bin/env python
# -*- coding: utf8 -*-

import select
import socket
import SocketServer
import struct

import logbook

import icmp

SERVER_ADDR = ("23.226.226.196", 1)

class ICMPServer(SocketServer.BaseServer):
    """Base class for various socket-based server classes.

    Defaults to synchronous IP stream (i.e., TCP).

    """

    address_family = socket.AF_INET

    socket_type = socket.SOCK_RAW

    protocol = socket.IPPROTO_ICMP

    request_queue_size = 5

    allow_reuse_address = True

    max_packet_size = 65536

    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
        """Constructor.  May be extended, do not override."""
        SocketServer.BaseServer.__init__(
            self, server_address, RequestHandlerClass)
        self.socket = socket.socket(
            self.address_family, self.socket_type,
            self.protocol)
        if bind_and_activate:
            self.server_bind()

    def server_bind(self):
        """Called by constructor to bind the socket.

        May be overridden.

        """
        if self.allow_reuse_address:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_address = SERVER_ADDR

    def fileno(self):
        """Return socket file number.

        Interface required by select().

        """
        return self.socket.fileno()

    def get_request(self):
        """Get the request and client address from the socket.

        May be overridden.

        """
        # data, client_addr = self.socket.recvfrom(self.max_packet_size)
        return self.socket, SERVER_ADDR


class ThreadedBaseServer(SocketServer.ThreadingMixIn, ICMPServer):
    pass


class ICMPRequestHandler(SocketServer.BaseRequestHandler):
    '''
    ICMP
    '''
    def handle(self):
        raw_data, client_addr = self.request.recvfrom(4096)
        identifier, sequence, raw_addr = icmp.unpack_reply(raw_data)
        print repr(raw_addr)
        remote_addr = eval(raw_addr)
        logbook.info("get the remote addr {}".format(remote_addr))

        remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote.connect(remote_addr)
        logbook.info("connect the remote server")

        fdset = [self.request, remote]
        r, w, e = select.select(fdset, [], [])

        while True:
            if self.request in r:
                locate_data, _ = self.request.recvfrom(4096)
                identifier, sequence, content = \
                    icmp.unpack_reply(locate_data)
                logbook.info("locate: {}".format(repr(locate_data)))
                result = remote.send(content)
                logbook.info("result: {}".format(result))
                if result <= 0:
                    logbook.info("breaking down")
                    break
            if remote in r:
                remote_data = remote.recv(4096)
                logbook.info("remote: {}".format(repr(remote_data)))
                packet = icmp.pack_reply(identifier, 0, remote_data)
                result = self.request.sendto(packet, client_addr)
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
