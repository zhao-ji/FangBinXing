#! /usr/bin/env python
# -*- coding: utf8 -*-

import select
import socket
import SocketServer
import struct

import logbook


class Socks5Server(SocketServer.StreamRequestHandler):
    '''
    Socks5 locate server
    '''
    def handle(self):
        # 1. Authorization
        # The SOCKS5 protocol is defined in RFC 1928
        auth_shake_1 = self.request.recv(262)
        self.request.send(b"\x05\x00")
        logbook.info(
            "auth shake: recieve {}  send {}"
            .format(repr(auth_shake_1), repr(b"\x05\x00"))
            )

        # 2. Request
        data = self.rfile.read(4)
        # first field: SOCKS version number, must be 0x05
        # second field: SOCKS command code, must be 0x01
        mode = ord(data[1])
        if mode != 1: # if not a TCP/IP stream connection
            reply = b"\x05\x07\x00\x01"  # Command not supported
            self.request.send(reply)
            logbook.error("Command not supported")
            return

        # third field: SOCKS reserved field, must be 0x00
        # fourth field: SOCKS address type, IPv4-address or Domain-name
        addrtype = ord(data[3])
        if addrtype == 1:       # IPv4
            # 4 bytes for IPv4 address
            addr = socket.inet_ntoa(self.rfile.read(4))
            logbook.info("ipv4 address: {}".format(addr))
        elif addrtype == 3:     # Domain name
            # 1 byte of name length followed by the name for Domain name
            domain_name_length = ord(self.rfile.read(1)[0])
            addr = self.rfile.read(domain_name_length)
            logbook.info("domain name is {}".format(addr))

        # port number in a network byte order, 2 bytes
        raw_port_data = self.rfile.read(2)
        port = struct.unpack('>H', raw_port_data)[0]
        logbook.info("request port is {}".format(port))

        # 3. Connect
        remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote.connect((addr, port))
        logbook.info("dist-app address {}:{}".format(addr, port))
        ret_addr, ret_port = remote.getsockname()
        logbook.info(
            "server-bind address: {}:{}".format(ret_addr, ret_port))

        # 4. Response
        reply_prefix = b"\x05\x00\x00\x01"

        # server response:
        #    field1: SOCKS protocol version, 1 byte
        #    field2: status, 1byte, 0x00 = request granted
        #    field3: reserved, must be 0x00

        #    field4: address type, 1 byte
        #       0x01 = IPv4 address
        #       0x03 = Domain name
        #    field6: network byte order port number, 2 bytes

        reply_suffix = b"{}{}".format(
            socket.inet_aton(ret_addr),
            struct.pack(">H", ret_port),
            )

        reply = b"{}{}".format(reply_prefix, reply_suffix)
        self.request.send(reply)

        self.process(self.request, remote)

    def process(self, local, remote):
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


def main():
    local_log = logbook.StderrHandler()
    local_log.format_string = (u'[{record.time:%H:%M:%S}] '
                               u'lineno:{record.lineno} '
                               u'{record.level_name}:{record.message}')
    local_log.push_application()

    logbook.info("start connecting...")
    server = SocketServer.ThreadingTCPServer(('0.0.0.0', 233), Socks5Server)
    logbook.info("start server at localhost in 233")
    server.serve_forever()


if __name__ == '__main__':
    main()
