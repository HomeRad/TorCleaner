# -*- coding: iso-8859-1 -*-
from wc import ip
configs = [
    [# numeric
     "1.2.3.4",
     "2.3.4",
     ".3.4",
     "3.4",
     ".4",
     "4",
    ],
    [# names
     "www.kampfesser.de",
     "q2345qwer9 u2 42ß3 i34 uq3tu ",
    ],
    [# network 1
     "192.168.1.1/8",
    ],
    [# network 2
     "192.168.1.1/16",
    ],
    [# network 3
     "192.168.1.1/24",
    ],
    [# network 4
     "192.168.1.1/255.255.255.0",
    ],
    [# network 5
     "192.168.1.1/255.255.0.0",
    ],
    [# ipv6
     "::0",
     "1::",
     "1::1",
     "fe00::0",
     "",
    ],
]

tests = [
    "1.2.3.4",
    "2.3.4",
    "192.168.1.18",
    "192.168.2.18",
    "192.169.2.18",
]
for config in configs:
    print "config", config
    hosts, nets = ip.hosts2map(config)
    for host in tests:
        print "ip", host, ip.host_in_set(host, hosts, nets)
