#!/usr/bin/env /usr/bin/python3

import argparse
import sys
from typing import Optional
from typing import Tuple
import re
import socket  # for validating IP-address


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
def parse_ip_netmask(argv=None) -> Tuple[int, int, int]:
    parser = argparse.ArgumentParser(description='IP addresses calculator')
    parser.add_argument('ip_dotted', type=str, help='IP-addres as string in dotted-decimal format, e.g. 192.168.1.1')
    parser.add_argument('mask', type=str, help='network mask either as prefix (/num) or as dotted-decimal string')
    parser.add_argument('subnets', type=int, help='the number of subnets to organize having base part of IP address')
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

    elif '.' in args.mask and is_valid_ip(args.mask):
        netmask = ip_str_to_int(args.mask)
    else:
        print("Wrong network mask: Temp stub for usage()")
        sys.exit()

    return ip, netmask, args.subnets


# calculate inverse network mask (in C/C++ it is just ~mask)
# возвращает маску с инверсными значениями битов
def wildcard(int_mask):
    """
    11111111 11111111 11111111 00000000
    xor (^)
    11111111 11111111 11111111 11111111
    =
    00000000 00000000 00000000 11111111
    """
    return int_mask ^ 0xFFFFFFFF


def get_network_ip(ip: 'int', mask: 'int') -> int:
    return ip & mask


def get_broadcast_ip(ip: 'int', mask: 'int') -> int:
    return ip | wildcard(mask)


def prefix_to_mask(pref: 'int') -> int:
    return ((1 << pref) - 1) << (32 - pref)


# Считает количество '1' в бинарном представлении целого числа
# Python 3.10 introduces int.bit_count()
# bin(value).count("1") for earlier versions of Python
def get_bit_count(value: 'int') -> int:
    count = 0
    while value:
        count += 1
        value &= value - 1
    return count


def mask_to_prefix(mask: 'int') -> int:
    return get_bit_count(mask)


# вычисляет новый префикс для заданного количества подсетей N_subnets, которые нужно создать
# new_prefix - old_prefix = количество бит, которые нужно перекинуть из хостовой части адреса в сетевую часть
# works ONLY for 'int'
def pref_by_subnets(base_prefix: int, n_subnets: int) -> Optional[int]:
    n_subnets -= 1
    n_subnets |= n_subnets >> 1
    n_subnets |= n_subnets >> 2
    n_subnets |= n_subnets >> 4
    n_subnets |= n_subnets >> 8
    n_subnets |= n_subnets >> 16

    # new_prefix = base_prefix + n_subnets.bit_count()
    new_prefix = base_prefix + get_bit_count(n_subnets)
    return new_prefix if new_prefix <= 32 else None


def main():
    # Нам нужно сгенерировать 10 подсетей из имеющегося базового адреса сети = 192.168.0.1/24
    # АЛГОРИТМ:
    # 1) понять сколько бит нам нужно перебросить из хостовой порции адреса в сетевую порцию адреса для создания
    #    нужного количества подсетей
    # 2) вычислить маску (префикс) для каждой подсети - к базовому префиксу добавить количество бит, переброшенных
    #    из хостовой порции адреса в сетевую порцию; получившийся префикс будет одинаковым для всех подсетей.
    # 3) для каждой из 10 подсетей нужно создать уникальные комбинации из тех битов, что были перенесены из хостовой
    #    части адреса в сетевую часть адреса. Для этого из новой маски для подсетей выделяем добавленную часть и
    #    последовательно эту часть инкрементируем для каждой последующей подсети
    # 4) в результате получаем сетевые адреса для каждой из 10 подсетей. Далее для каждой подсети вычисляем:
    #    broadcast_ip, first_ip, last_ip, range_ip
    # Нужно сгенерировать файл для dhcpd по такому шаблону:
    """
subnet 172.16.8.0 netmask 255.255.252.0 {
        authoritative;
        option domain-name-servers 8.8.4.4, 8.8.8.8;
        option routers 172.16.8.1;
        option subnet-mask 255.255.252.0;
}

pool { allow members of "users" "cl-floor1-0"; deny dynamic bootp clients; range 172.16.8.2; }
pool { allow members of "users" "cl-floor1-1"; deny dynamic bootp clients; range 172.16.8.3; }
pool { allow members of "users" "cl-floor1-2"; deny dynamic bootp clients; range 172.16.8.4; }
...
pool { allow members of "users" "cl-floor0-n"; deny dynamic bootp clients; range 172.16.8.254; }
    """

    ip, netmask, n_subnets = parse_ip_netmask(sys.argv)

    net_ip = get_network_ip(ip, netmask)
    broadcast_ip = get_broadcast_ip(ip, netmask)
    net_prefix = mask_to_prefix(netmask)

    # теперь мы можем вычислить, какой префикс и какая маска будет у каждой из 10 подсетей (он будет одинаковый)
    subnets_prefix = pref_by_subnets(net_prefix, n_subnets)
    subnet_mask = prefix_to_mask(subnets_prefix)

    prev_subnet_ip = net_ip
    # генерируем уникальные сетевые порции для каждой из 10 подсетей
    for subnet_id in range(n_subnets):  # при N = 10, subnet_id = [0;14]

        # адрес первой подсети будет точно такой же, как и адрес базовой сети (при этом маска подсети будет другой)
        if subnet_id == 0:
            subnet_ip = net_ip
        else:
            host_bits = 32 - subnets_prefix
            subnet_ip = ((prev_subnet_ip >> host_bits) + 1) << host_bits
        prev_subnet_ip = subnet_ip
        subnet_bcast_ip = get_broadcast_ip(subnet_ip, subnet_mask)
        first_ip_in_subnet = subnet_ip + 1  # адрес первого устройства в текущей подсети
        print(f'{ip_int_to_str(subnet_ip)}/{subnets_prefix}')

        # To escape curly braces we need to double the {{ and }} inside f-string
        s = f"""subnet {ip_int_to_str(subnet_ip)} netmask {ip_int_to_str(subnet_mask)} {{
                authoritative;
                option domain-name-servers 8.8.4.4, 8.8.8.8;
                option routers {ip_int_to_str(first_ip_in_subnet)};
                option subnet-mask {ip_int_to_str(subnet_mask)};
        }}\n"""

        # теперь нам нужно создать такое количество файлов, которое будет соответствовать количеству подсетей
        with open(f'test_{subnet_id}.net', 'w') as f:
            f.write(s)
            # диапазон адресов устройств в пределах текущей подсети
            client_ip_range = range(subnet_ip+2, subnet_bcast_ip)

            for i, ip in enumerate(client_ip_range):
                f.write(f'pool {{ allow members of "users" "cl-floor{subnet_id}-{i}";'
                        f' deny dynamic bootp clients; range {ip_int_to_str(ip)}; }}\n')

    print('Done!')


if __name__ == "__main__":
    main()
