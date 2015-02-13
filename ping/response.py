#! /usr/bin/env python
# -*- coding: utf8 -*-

import socket

import logbook

import icmp

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
        raw_data, addr = sock.recvfrom(4096)
        logbook.info(addr)
        identifier, data = icmp.unpack_reply(raw_data)
        logbook.info(
            "the identifier is {}".format(repr(identifier)))
        logbook.info("the data is {}".format(repr(data)))
        packet_will_be_sent = icmp.pack_reply(33, data)
        ret = sock.sendto(packet_will_be_sent, addr)
        # packet = icmp.pack_reply_with_scapy(
        #     dst_ip=addr[0], identifier=45, content=data)
        # ret = sock.sendto(packet, addr)
        logbook.info("send {} bytes data".format(ret))
