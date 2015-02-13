#! /usr/bin/env python
# -*- coding: utf8 -*-

import socket

import logbook

#SERVER_ADDR = "23.226.226.196"
SERVER_ADDR = "23.252.105.45"

def ping(content):
    packet = header + content

    sock.sendto(packet, (SERVER_ADDR, 0))
    return sock.recv(4096)


if __name__ == "__main__":
    # the public network interface
    HOST = socket.gethostbyname(socket.gethostname())

    # create a raw socket and bind it to the public interface
    sock = socket.socket(
        socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    sock.bind((HOST, 0))

    while True:
        raw_data, addr = s.recvfrom(65565)
        logbook.info(addr)
        data = icmp.unpack_reply(raw_data)
        packet_will_be_sent = icmp.pack_reply(data)
        ret = sock.sendto(packet_will_be_sent, addr)
        logbook.info(ret)
