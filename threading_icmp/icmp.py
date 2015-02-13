#! /usr/bin/env python
# -*- coding: utf8 -*-

import os
import socket
import struct
import sys

import logbook

ICMP_ECHO_REPLY = 0
ICMP_ECHO_REQUEST = 8


def carry_around_add(a, b):
    c = a + b
    return (c & 0xffff) + (c >> 16)

def checksum(msg):
    # filed with zero if the length of msg is odd
    if len(msg)%2 is 1:
        msg += b'\x00'
    # process the internet checksum
    s = 0
    for i in range(0, len(msg), 2):
        w = ord(msg[i]) + (ord(msg[i+1]) << 8)
        s = carry_around_add(s, w)
    # make the result in big endian
    answer = ~s & 0xffff
    return answer >> 8 | (answer << 8 & 0xff00)

def pack(data):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    my_checksum = 0
    my_ID = os.getpid() & 0xFFFF
    logbook.info(my_ID)

    # Make a dummy heder with a 0 checksum.
    header = struct.pack(
        "bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, my_ID, 1)

    # Calculate the checksum on the data and the dummy header.
    my_checksum = checksum(header + data)

    # Now that we have the right checksum, we put that in.
    # It's just easier to make up a new header
    # than to stuff it into the dummy.
    header = struct.pack(
        "bbHHh", ICMP_ECHO_REQUEST, 0,
        socket.htons(my_checksum), my_ID, 1,
        )

    return header + data

def pack_reply(data):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    my_checksum = 0
    my_ID = os.getpid() & 0xFFFF
    logbook.info(my_ID)

    # Make a dummy heder with a 0 checksum.
    header = struct.pack(
        "bbHHh", ICMP_ECHO_REPLY, 0, my_checksum, my_ID, 1)

    # Calculate the checksum on the data and the dummy header.
    my_checksum = checksum(header + data)

    # Now that we have the right checksum, we put that in.
    # It's just easier to make up a new header
    # than to stuff it into the dummy.
    header = struct.pack(
        "bbHHh", ICMP_ECHO_REPLY, 0,
        socket.htons(my_checksum), my_ID, 1,
        )

    return header + data

def unpack(data):
    logbook.info("identifier is {}".format(ord(data[4:6])))
    return data[8:]
