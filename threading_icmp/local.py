#! /usr/bin/env python
# -*- coding: utf8 -*-

import select
import socket
import SocketServer
import struct

import logbook

import icmp

REMOTE_ADDR = ("chashuibiao.org", 1)


class Socks5Server(SocketServer.StreamRequestHandler):
    '''
    Socks5 locate server
    '''
    def handle(self):
        # 1. Authorization
        self.request.recv(262)
        self.request.send(b"\x05\x00")

        # 2. Request
        data = self.request.recv(4)
        mode = ord(data[1])
        if mode != 1: # if not a TCP/IP stream connection
            reply = b"\x05\x07\x00\x01"  # Command not supported
            self.request.send(reply)
            return

        addrtype = ord(data[3])
        if addrtype == 1:       # IPv4
            # 4 bytes for IPv4 address
            addr = socket.inet_ntoa(self.request.recv(4))
            logbook.info("ipv4 address: {}".format(addr))
        elif addrtype == 3:     # Domain name
            # 1 byte of name length followed by the name for Domain name
            addr = self.request.recv(ord(self.request.recv(1)))
            logbook.info("domain name is {}".format(addr))

        # port number in a network byte order, 2 bytes
        port = struct.unpack('>H', self.request.recv(2))[0]
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
        remote = socket.socket(
            socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        identifier = self.client_address[1]
        goal_addr = (addr, port)
        init_packet = icmp.pack(identifier, 0, repr(goal_addr))
        remote.sendto(init_packet, REMOTE_ADDR)
        _ = icmp.unpack(remote.recv(4096))
        logbook.info("first handshake reply: {}".format(_))

        # 5. Communicate
        self.process(self.request, remote)

    def process(self, local, remote):
        fdset = [local, remote]
        while True:
            r, w, e = select.select(fdset, [], [])
            if local in r:
                logbook.info("local send")
                identifier = self.client_address[1]
                logbook.info("identifier: {}".format(identifier))
                local_data = local.recv(4096)
                logbook.info("local data: {}".format(repr(local_data)))
                if len(local_data) > 0:
                    packet = icmp.pack(identifier, 0, local_data)
                    remote.sendto(packet, REMOTE_ADDR)
            if remote in r:
                logbook.info("remote send")
                if local.send(icmp.unpack(remote.recv(4096))) <= 0:
                    logbook.info("remote breaking down")
                    break


def main():
    local_log = logbook.StderrHandler()
    local_log.format_string = (u'[{record.time:%H:%M:%S}] '
                               u'lineno:{record.lineno} '
                               u'{record.level_name}:{record.message}')
    local_log.push_application()

    logbook.info("start connecting...")
    server = SocketServer.ThreadingTCPServer(('', 777), Socks5Server)
    logbook.info("start server at localhost in 777")
    server.serve_forever()


if __name__ == '__main__':
    main()
