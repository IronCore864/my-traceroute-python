#!/usr/bin/env python3
import socket
import os
import struct
import time
import argparse
from collections import defaultdict

MAX_HOPS = 64
PROBES_PER_HOP = 3
WAIT = 5.0

ICMP_ECHO_REQUEST = 8


def _checksum(data):
    data = bytearray(data)
    csum = 0
    countTo = (len(data) / 2) * 2
    count = 0
    while count < countTo:
        this_val = data[count + 1] * 256 + data[count]
        csum = csum + this_val
        csum = csum & 0xffffffff
        count = count + 2
    if countTo < len(data):
        csum = csum + data[len(data) - 1]
        csum = csum & 0xffffffff
    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def _receive(my_socket, timeout):
    start_time = time.time()
    while (start_time + timeout - time.time()) > 0:
        try:
            received_packet, (addr, x) = my_socket.recvfrom(1024)
        except socket.timeout:
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

    return None, None, None


def _send(my_socket, dst_ip, id):
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, 0, id, 1)
    data = struct.pack("d", time.time())
    check_sum = _checksum(header + data)
    # Convert 16-bit integers from host to network  byte order
    check_sum = socket.htons(check_sum)
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, check_sum, id, 1)
    packet = header + data
    my_socket.sendto(packet, (dst_ip, 1))


def _ping(dst_ip, timeout, ttl):
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
    my_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
    my_socket.settimeout(timeout)
    # Use PID for header id
    id = os.getpid() & 0xFFFF  # Return the current process i
    _send(my_socket, dst_ip, id)
    time_used, host, dest_reached = _receive(my_socket, timeout)
    my_socket.close()
    return time_used, host, dest_reached


def _output_one_hop(d):
    res = ""
    for host, times in d.items():
        time_list = ", ".join(['' if not i else str(i) + "ms" for i in times])
        res += "{}, {}".format(host, time_list)
    print(res)


def traceroute(host, timeout, max_hops):
    dst_ip = socket.gethostbyname(host)
    all_hops = []
    # Loop through max_hops
    for ttl in range(1, max_hops + 1):
        d = defaultdict(list)
        # Loop through PROBES_PER_HOP
        for i in range(PROBES_PER_HOP):
            time_used, host, dest_reached = _ping(dst_ip, timeout, ttl)
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
    traceroute(args.hostname, WAIT, MAX_HOPS)
