""" ip related utility functions """

import re

# IP Adress regular expressions
_ipv4_num = r"\d{1,3}"
_ipv4_num_4 = (_ipv4_num,)*4
_ipv4_re = re.compile(r"^%s\.%s\.%s\.%s$" % _ipv4_num_4)
# see rfc2373
_ipv6_num = r"[\da-f]{1,4}"
_ipv6_re = re.compile(r"^%s:%s:%s:%s:%s:%s:%s:%s$" % ((_ipv6_num,)*8))
_ipv6_ipv4_re = re.compile(r"^%s:%s:%s:%s:%s:%s:" % ((_ipv6_num,)*6) + \
                           r"%s\.%s\.%s\.%s$" % _ipv4_num_4)
_ipv6_abbr_re = re.compile(r"^((%s:){0-6}%s)?::((%s:){0-6}%s)?$" % \
                           ((_ipv6_num,)*4))
_ipv6_ipv4_abbr_re = re.compile(r"^((%s:){0-4}%s)?::((%s:){0-5})?" % \
                           ((_ipv6_num,)*3) + \
                           "%s\.%s\.%s\.%s$" % _ipv4_num_4)

def ipv6_expand (ip, num):
    """expand an IPv6 address with included :: to num octets"""
    i = ip.find("::")
    prefix = ip[:i]
    suffix = ip[i+2:]
    count = prefix.count(":") + suffix.count(":")
    if prefix: prefix = prefix+":"
    if suffix: suffix = ":"+suffix
    if count>=num: raise ValueError, "invalid ipv6 number: %s"%ip
    fill = (num-count-1)*"0:" + "0"
    return prefix+fill+suffix


def expand (ip):
    if _ipv4_re.match(ip) or \
       _ipv6_re.match(ip) or \
       _ipv6_ipv4_re.match(ip):
        return ip
    if _ipv6_abbr_re.match(ip):
        return ipv6_expand(ip, 8)
    if _ipv6_ipv4_abbr_re.match(ip):
        i = ip.rfind(":") + 1
        return ipv6_expand(ip[:i], 6) + ip[i:]
    return ip


def is_numeric (ip):
    return _ipv4_re.match(ip) or \
           _ipv6_re.match(hostname) or \
           _ipv6_ipv4_re.match(hostname) or \
           _ipv6_abbr_re.match(hostname) or \
           _ipv6_ipv4_abbr_re.match(hostname)

# from the python cookbook:
# IP address manipulation functions, dressed up a bit

import socket, struct

def dottedQuadToNum (ip):
    "convert decimal dotted quad string to long integer"
    return struct.unpack('!L', socket.inet_aton(ip))[0]

def numToDottedQuad (n):
    "convert long int to dotted quad string"
    return socket.inet_ntoa(struct.pack('!L', n))

def makeMask (n):
    "return a mask of n bits as a long integer"
    return (2L<<n-1)-1

def ipToNetAndHost (ip, maskbits):
    "returns tuple (network, host) dotted-quad addresses given IP and mask size"
    # (by Greg Jorgensen)
    n = dottedQuadToNum(ip)
    m = makeMask(maskbits)
    host = n & m
    net = n - host
    return numToDottedQuad(net), numToDottedQuad(host)

