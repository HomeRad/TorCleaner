""" ip related utility functions """
# -*- coding: iso-8859-1 -*-

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import re, socket, struct, math
from sets import Set
from log import *

# IP Adress regular expressions
_ipv4_num = r"\d{1,3}"
_ipv4_num_4 = r"%s\.%s\.%s\.%s" % ((_ipv4_num,)*4)
_ipv4_re = re.compile(r"^%s$" % _ipv4_num_4)
# see rfc2373
_ipv6_num = r"[\da-f]{1,4}"
_ipv6_re = re.compile(r"^%s:%s:%s:%s:%s:%s:%s:%s$" % ((_ipv6_num,)*8))
_ipv6_ipv4_re = re.compile(r"^%s:%s:%s:%s:%s:%s:" % ((_ipv6_num,)*6) + \
                           r"%s$" % _ipv4_num_4)
_ipv6_abbr_re = re.compile(r"^((%s:){0,6}%s)?::((%s:){0,6}%s)?$" % \
                            ((_ipv6_num,)*4))
_ipv6_ipv4_abbr_re = re.compile(r"^((%s:){0,4}%s)?::((%s:){0,5})?" % \
                           ((_ipv6_num,)*3) + \
                           "%s$" % _ipv4_num_4)
# netmask regex
_host_netmask_re = re.compile(r"^%s/%s$" % (_ipv4_num_4, _ipv4_num_4))
_host_bitmask_re = re.compile(r"^%s/\d{1,2}$" % _ipv4_num_4)


def expand_ipv6 (ip, num):
    """expand an IPv6 address with included :: to num octets
       raise ValueError on invalid IP addresses
    """
    i = ip.find("::")
    prefix = ip[:i]
    suffix = ip[i+2:]
    count = prefix.count(":") + suffix.count(":")
    if prefix:
        count += 1
        prefix = prefix+":"
    if suffix:
        count += 1
        suffix = ":"+suffix
    if count>=num: raise ValueError("invalid ipv6 number: %s"%ip)
    fill = (num-count-1)*"0:" + "0"
    return prefix+fill+suffix


def expand_ip (ip):
    """ipv6 addresses are expanded to full 8 octets, all other
       addresses are left untouched
       return a tuple (ip, num) where num==1 if ip is a numeric ip, 0
       otherwise.
    """
    if _ipv4_re.match(ip) or \
       _ipv6_re.match(ip) or \
       _ipv6_ipv4_re.match(ip):
        return (ip, 1)
    if _ipv6_abbr_re.match(ip):
        return (expand_ipv6(ip, 8), 1)
    if _ipv6_ipv4_abbr_re.match(ip):
        i = ip.rfind(":") + 1
        return (expand_ipv6(ip[:i], 6) + ip[i:], 1)
    return (ip, 0)


def is_valid_dq (ip):
    if not _ipv4_re.match(ip): return
    a,b,c,d = [int(i) for i in ip.split(".")]
    return a<=255 and b<=255 and c<=255 and d<=255


def is_valid_bitmask (mask):
    return 1<=mask<=32


def dq2num (ip):
    "convert decimal dotted quad string to long integer"
    return struct.unpack('!L', socket.inet_aton(ip))[0]


def num2dq (n):
    "convert long int to dotted quad string"
    return socket.inet_ntoa(struct.pack('!L', n))


def suffix2mask (n):
    "return a mask of n bits as a long integer"
    return (2L<<n-1)-1


def mask2suffix (mask):
    """return suff for given bit mask"""
    return int(math.log(mask+1, 2))


def dq2mask (ip):
    "return a mask of bits as a long integer"
    n = dq2num(ip)
    return -((-n+1) | n)


def dq2net (ip, mask):
    n = dq2num(ip)
    net = n - (n & mask)
    return (net, mask)


def dq_in_net (n, net, mask):
    """return 1 iff numerical ip n is in given net with mask.
       (net,mask) must be returned previously by ip2net"""
    m = n - (n & mask)
    return m==net


def host_in_set (ip, hosts, nets):
    if ip in hosts:
        return True
    if is_valid_dq(ip):
        n = dq2num(ip)
        for net, mask in nets:
            if dq_in_net(n, net, mask):
                return True
    return False


def strhosts2map (strhosts):
    return hosts2map([s.strip() for s in strhosts.split(",") if s])


def hosts2map (hosts):
    """return a set of named hosts, and a list of subnets (host/netmask
       adresses).
       Only IPv4 host/netmasks are supported.
    """
    hostset = Set()
    nets = []
    for host in hosts:
        if _host_bitmask_re.match(host):
            host, mask = host.split("/")
            mask = int(mask)
            if not is_valid_bitmask(mask):
                error(WC, "bitmask %d is not a valid network mask", mask)
                continue
            if not is_valid_dq(host):
                error(WC, "host %s is not a valid ip address", host)
                continue
            nets.append(dq2net(host, suffix2mask(mask)))
        elif _host_netmask_re.match(host):
            host, mask = host.split("/")
            if not is_valid_dq(host):
                error(WC, "host %s is not a valid ip address", host)
                continue
            if not is_valid_dq(mask):
                error(WC, "mask %s is not a valid ip network mask", mask)
                continue
            nets.append(dq2net(host, dq2mask(mask)))
        else:
            hostset.add(host)
    return (hostset, nets)


def map2hosts (hostmap):
    ret = hostmap[0].copy()
    for net, mask in hostmap[1]:
        ret.add("%s/%d" % (net, mask2suffix(mask)))
    return ret


def _test ():
    hosts, nets = hosts2map(["192.168.1.1/16"])
    for net, mask in nets:
        print num2dq(net), mask2suffix(mask)

if __name__=='__main__':
    _test()
