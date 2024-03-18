#!/usr/bin/env /usr/bin/python3

# ipcalc_v2 with parsing arguments

import argparse
import sys
from typing import Optional
from typing import Tuple
import re
import socket

# TODO: add and implement following options:
# --net
# --bcast
# --first
# --last
# --range     [1st_ip; last_ip]
# --bordered  11000000.10101000.00000001.01|001001

# ipcalc -a
# ipcalc --all


# convert an IP address from string in dotted decimal format to flat integer number
def ip_str_to_int(str_ip) -> Optional[int]:
    lst_str_ip = str_ip.split('.')
    if (len(lst_str_ip)) != 4:
        return None

    octs = [int(x) for x in lst_str_ip]
    for octet in octs:
        if octet not in range(0, 255 + 1):
            return None

    return (octs[0] << 24 |
            octs[1] << 16 |
            octs[2] << 8 |
            octs[3] << 0)


# convert IP address from flat integer number to string in dotted decimal format
def ip_int_to_str(int_ip) -> str:
    if not 0x00 <= int_ip <= 0xFFFFFFFF:
        print("Invalid decimal value for IP-address: int_ip")
        sys.exit()
    # 0xFF = 00000000.00000000.00000000.11111111
    return (str((int_ip >> 24) & 0xFF) + '.' +
            str((int_ip >> 16) & 0xFF) + '.' +
            str((int_ip >> 8) & 0xFF) + '.' +
            str((int_ip >> 0) & 0xFF))


def is_valid_ip(ip_str_dotted):
    pattern = r"(((25[0-5])|(2[0-4]\d)|(1\d{2})|(\d{1,2}))\.){3}(((25[0-5])|(2[0-4]\d)|(1\d{2})|(\d{1,2})))"
    return True if re.fullmatch(pattern, ip_str_dotted) else False


def is_valid_ip_v2(ip_str_dotted):
    try:
        socket.inet_aton(ip_str_dotted)
        return True
    except:
        return False


# returns tuple of (ip, netmask), both of int type
def parse_ip_netmask(argv=None) -> Tuple[int, int]:
    parser = argparse.ArgumentParser(description='IP addresses calculator')
    parser.add_argument('ip_dotted', type=str, help='IP-addres as string in dotted-decimal format, e.g. 192.168.1.1')
    parser.add_argument('mask', type=str, help='network mask either as prefix (/num) or as dotted-decimal string')
    args = parser.parse_args()

    if is_valid_ip_v2(args.ip_dotted):
        ip = ip_str_to_int(args.ip_dotted)
    else:
        print("Wrong IP-address: Temp stub for usage()")
        sys.exit()

    if '/' in args.mask:
        if not 0 <= int(args.mask[1:]) <= 32:
            print("Wrong prefix: Temp stub for usage()")
            sys.exit()

        ones = int(args.mask[1:])
        zeroes = 32 - ones
        netmask = int(('1' * ones + '0' * zeroes), 2)

    elif '.' in args.netmask and is_valid_ip(args.mask):
        netmask = ip_str_to_int(args.mask)
    else:
        print("Wrong network mask: Temp stub for usage()")
        sys.exit()

    return ip, netmask


def wildcard(netmask: 'int') -> [int]:
    """
    11111111 11111111 11111111 00000000
    xor (^)
    11111111 11111111 11111111 11111111
    =
    00000000 00000000 00000000 11111111
    """
    return netmask ^ 0xFFFFFFFF


def main():
    ip, netmask = parse_ip_netmask(sys.argv)
    net_ip = ip & netmask
    broadcast_ip = ip | wildcard(netmask)


    print(f"{'ip':<9} = {ip_int_to_str(ip)}")
    print(f"{'netmask':<9} = {ip_int_to_str(netmask)}")
    print(f"{'net_ip':<9} = {ip_int_to_str(ip & netmask)}")

    print("##################################################")

    print(f"{'bcast_ip':<9} = {ip_int_to_str(broadcast_ip)}")
    print(f"{'first_ip':<9} = {ip_int_to_str(net_ip + 1)}")
    print(f"{'last_ip':<9} = {ip_int_to_str(broadcast_ip - 1)}")


if __name__ == "__main__":
    main()
