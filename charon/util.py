# -*- coding: utf-8 -*-

import os
import sys
import time
import fcntl
import base64
import socket
import struct

devnull = open(os.devnull, 'rw')

def check_wait(test, initial=10, factor=1, max_tries=60):
    """Call function ‘test’ periodically until it returns True or a timeout occurs."""
    wait = initial
    tries = 0
    while tries < max_tries and not test():
        time.sleep(wait)
        wait = wait * factor
        tries = tries + 1
        if tries == max_tries:
            raise Exception("operation timed out")
    return True

def generate_random_string(length=256):
    """Generate a base-64 encoded cryptographically strong random string."""
    f = open("/dev/urandom", "r")
    s = f.read(length)
    assert len(s) == length
    return base64.b64encode(s)

def make_non_blocking(fd):
    fcntl.fcntl(fd, fcntl.F_SETFL, fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NONBLOCK)

def ping_tcp_port(ip, port, timeout=1):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
    try:
        s.connect((ip, port))
    except:
        # FIXME: check that the timeout expired or we got a refused
        # connection. For any other error, throw an exception.
        return False
    s.shutdown(socket.SHUT_RDWR)
    return True

def wait_for_tcp_port(ip, port, timeout=-1, open=True, callback=None):
    """Wait until the specified TCP port is open or closed."""
    n = 0
    while True:
        if ping_tcp_port(ip, port) == open: return True
        n = n + 1
        if timeout != -1 and n >= timeout: break
        time.sleep(1) # FIXME - ping_tcp_port() *may* also wait 1 second
        if callback: callback()
    raise Error("timed out waiting for port {0} on ‘{1}’".format(port, ip))

def ansi_warn(s):
    return "\033[1;31m" + s + "\033[0m" if sys.stderr.isatty() else s
