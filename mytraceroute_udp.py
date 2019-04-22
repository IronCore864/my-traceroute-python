#!/usr/bin/env python3
import socket
import os
import struct
import time
import argparse
from collections import defaultdict
import random

MAX_HOPS = 64
PROBES_PER_HOP = 3
PORT_RANGE_LO = 33434
PORT_RANGE_HI = PORT_RANGE_LO + PROBES_PER_HOP * MAX_HOPS
ICMP_ECHO_REQUEST = 8


def _receive(my_socket):
    start_time = time.time()
    while True:
        try:
            received_packet, (addr, x) = my_socket.recvfrom(1024)
        except socket.timeout:
            print("timeout")
            break
        time_used = round((time.time() - start_time) * 1000, 3)
        icmp_header = received_packet[20:28]
        icmp_type, code, check_sum, packet_id, sequence = struct.unpack("bbHHh", icmp_header)
        try:
            host = socket.gethostbyaddr(addr)[0]
        except socket.herror:
            host = addr
        if icmp_type == 11 and code == 0:
            return time_used, host, None
        elif icmp_type == 0 and code == 0:
            return time_used, host, 'DEST_REACHED'


def _send(my_socket, dst_ip):
    my_socket.sendto(b'', (dst_ip, 1))


def _ping(dst_ip, ttl):
    sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.getprotobyname("udp"))
    sender_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
    _send(sender_socket, dst_ip)

    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
    port = random.choice(range(PORT_RANGE_LO, PORT_RANGE_HI))
    receiver_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    receiver_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    receiver_socket.bind(('', port))
    time_used, host, dest_reached = _receive(receiver_socket)

    sender_socket.close()
    receiver_socket.close()
    return time_used, host, dest_reached


def _output_one_hop(d):
    res = ""
    for host, times in d.items():
        time_list = ", ".join(['' if not i else str(i) + "ms" for i in times])
        res += "{}, {} ".format(host, time_list)
    print(res)


def traceroute(host, max_hops):
    dst_ip = socket.gethostbyname(host)
    all_hops = []
    # Loop through max_hops
    for ttl in range(1, max_hops + 1):
        d = defaultdict(list)
        # Loop through PROBES_PER_HOP
        for i in range(PROBES_PER_HOP):
            time_used, host, dest_reached = _ping(dst_ip, ttl)
            d[host].append(time_used)
            if time_used is not None:
                all_hops.append([time_used, host])
        _output_one_hop(d)
        if dest_reached == 'DEST_REACHED':
            break
    all_hops = sorted(all_hops)
    print("Slowest: {}ms {}".format(all_hops[-1][0], all_hops[-1][1]))


if __name__ == '__main__':
    if not os.geteuid() == 0:
        print("You need to be root to run this program!")
        exit(1)
    parser = argparse.ArgumentParser()
    parser.add_argument("hostname", help="the hostname you want to trace")
    args = parser.parse_args()
    traceroute(args.hostname, MAX_HOPS)
