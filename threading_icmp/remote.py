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

    # global socket dict
    demultiplexer = {}

    while True:
        raw_data, addr = sock.recvfrom(4096)
        logbook.info("the send address is {}".format(addr))
        identifier, sequence, content = icmp.unpack_reply(raw_data)
        logbook.info(
            "identifier: {}, sequence: {}, keys: {}"
            .format(identifier, sequence, demultiplexer.keys()))
        if identifier not in demultiplexer:
            continue

        if sequence == 6666:
            # start connect the web app server
            remote_addr = eval(content)
            remote = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            remote.connect(remote_addr)
            logbook.info(
                "connect the remote server: {}".format(remote_addr))

            demultiplexer[identifier] = remote
            packet = icmp.pack_reply(
                identifier, sequence, "ok")
            sock.sendto(packet, addr)
        elif sequence == 8888:
            # start exchange the data between the two side
            remote = demultiplexer[identifier]
            logbook.info("the http body: {}".format(raw_data))
            send_length = remote.send(raw_data)
            logbook.info(send_length)
            # remote_recv = remote.recv(1024)
            remote_recv = ''
            while True:
                buf = remote.recv(1024)
                if not len(buf):
                    break
                remote_recv += buf
            logbook.info("remote_recv: {}".format(remote_recv))
            packet = icmp.pack_reply(
                identifier, sequence, remote_recv)
            sock.sendto(packet, addr)
        else:
            logbook.info(
                "some situation occur, raw_data: {}"
                .format(raw_data))
