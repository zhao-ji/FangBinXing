#!/usr/bin/env python
# -*- coding: utf8 -*-

import select
import socket
import SocketServer
import struct

import logbook

import icmp
from ThreadedICMPServer import ThreadedICMPServer

# global socket dict: identifier and tcp-stream-socket
demultiplexer = {}

class ICMPRequestHandler(SocketServer.BaseRequestHandler):
    '''
    ICMP
    '''
    def handle(self):
        raw_data, local = self.request
        identifier, sequence, content = icmp.unpack_reply(raw_data)
        logbook.info("identifier: {} sequence: {}"
                     .format(identifier, sequence))

        if sequence == 6666:
            remote_addr = eval(content)
            remote = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            remote.connect(remote_addr)
            logbook.info(
                "connect the remote server: {}".format(remote_addr))

            global demultiplexer
            demultiplexer[identifier] = remote

            icmp_body = 'ok'
        elif sequence == 8888:
            if identifier not in demultiplexer:
                packet = icmp.pack_reply(
                    identifier, sequence, content)
                local.sendto(packet, self.client_address)

            remote = demultiplexer[identifier]

            if len(content) == 0:
                remote.close()
                demultiplexer.pop(identifier, 0)

            logbook.info("the http body:\n\n{}".format(content))
            remote.send(content)

            remote_recv = ''
            while True:
                buf = remote.recv(1024)
                if buf:
                    remote_recv += buf
                else:
                    break
            logbook.info("remote_recv: {}".format(remote_recv))
            icmp_body = remote_recv
        else:
            logbook.info("some situation occur, content:\n{}"
                         .format(content))
            icmp_body = content

        packet = icmp.pack_reply(identifier, sequence, icmp_body)
        local.sendto(packet, self.client_address)


if __name__ == '__main__':
    local_log = logbook.StderrHandler()
    local_log.format_string = (
        u'[{record.time:%H:%M:%S}] '
        u'lineno:{record.lineno} '
        u'{record.level_name}:{record.message}')
    local_log.push_application()

    server = ThreadedICMPServer(('0.0.0.0', 1), ICMPRequestHandler)
    logbook.info("start ICMP server")
    server.serve_forever()
