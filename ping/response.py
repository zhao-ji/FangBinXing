#! /usr/bin/env python
# -*- coding: utf8 -*-

import socket

import logbook

import icmp

if __name__ == "__main__":
    # the public network interface
    HOST = socket.gethostbyname(socket.gethostname())

    # create a raw socket and bind it to the public interface
    sock = socket.socket(
        socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    sock.bind((HOST, 0))
    logbook.info("the server start working")

    while True:
        raw_data, addr = sock.recvfrom(4096)
        logbook.info("the send address is {}".format(addr))
        identifier, sequence, content = icmp.unpack_reply(raw_data)
        logbook.info(
            "identifier: {}, sequence: {}, data: {}"
            .format(identifier, sequence, content))
        packet_will_be_sent = icmp.pack_reply(
            identifier, sequence, content*2)
        ret = sock.sendto(packet_will_be_sent, (addr[0], 1))
