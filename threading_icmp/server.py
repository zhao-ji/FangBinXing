#!/usr/bin/env python
# -*- coding: utf8 -*-

import select
import socket
import SocketServer
import struct

import logbook

import icmp

SERVER_ADDR = ("23.226.226.196", 1)
GLOBAL_DICT = {}

class ICMPServer(SocketServer.BaseServer):
    """Base class for various socket-based server classes.

    Defaults to synchronous IP stream (i.e., TCP).

    """

    address_family = socket.AF_INET

    socket_type = socket.SOCK_RAW

    protocol = socket.IPPROTO_ICMP

    request_queue_size = 5

    allow_reuse_address = True

    max_packet_size = 8192

    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=False):
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
        data, client_addr = self.socket.recvfrom(self.max_packet_size)
        return (data, self.socket), client_addr


class ThreadedBaseServer(SocketServer.ThreadingMixIn, ICMPServer):
    pass


class ICMPRequestHandler(SocketServer.BaseRequestHandler):
    '''
    ICMP
    '''
    def handle(self):
        raw_data, self.request = self.request
        identifier, sequence, raw_data = icmp.unpack_reply(raw_data)
        logbook.info(
            "identifier: {} sequence: {}"
            .format(identifier, sequence)
            )

        if sequence == 6666:
            # start connect the web app server
            remote_addr = eval(raw_data)
            remote = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            remote.connect(remote_addr)
            logbook.info(
                "connect the remote server: {}".format(remote_addr))

            global GLOBAL_DICT
            GLOBAL_DICT[identifier] = remote
            logbook.warn("GLOBAL_DICT: {}".format(GLOBAL_DICT))

            packet = icmp.pack_reply(
                identifier, sequence, "ok")
            self.request.sendto(packet, self.client_address)

        elif sequence == 8888:
            # start exchange the data between the two side
            remote = GLOBAL_DICT[identifier]
            logbook.info("the http body: {}".format(raw_data))
            logbook.info("remote: {}".format(remote))
            remote.send(raw_data)
            remote_recv = ''
            while True:
                buf = remote.recv(1024)
                if not len(buf):
                    break
                remote_recv += buf
            logbook.info("remote_recv: {}".format(remote_recv))
            packet = icmp.pack_reply(
                identifier, sequence, remote_recv)
            self.request.sendto(packet, self.client_address)

        else:
            logbook.info(
                "some situation occur, raw_data: {}"
                .format(raw_data))


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
    logbook.info("start ICMP server")
    server.serve_forever()


if __name__ == '__main__':
    main()
