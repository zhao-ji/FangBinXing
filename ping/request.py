#! /usr/bin/env python
# -*- coding: utf8 -*-

import socket

import logbook

import icmp

SERVER_ADDR = "23.226.226.196"
# SERVER_ADDR = "23.252.105.45"


def ping(content):
    packet = icmp.pack(content)
    sock.sendto(packet, (SERVER_ADDR, 0))
    return icmp.unpack(sock.recv(4096))


if __name__ == "__main__":
    sock = socket.socket(
        socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

    while 1:
        command = raw_input("please input:\n")
        if command == "quit":
            break
        else:
            ret = ping(command)
            print repr(ret)
