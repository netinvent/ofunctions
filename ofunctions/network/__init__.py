#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# This file is part of ofunctions package

"""
ofunctions is a general library for basic repetitive tasks that should be no brainers :)

Versioning semantics:
    Major version: backward compatibility breaking changes
    Minor version: New functionality
    Patch version: Backwards compatible bug fixes

"""

__intname__ = "ofunctions.network"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2014-2023 Orsiris de Jong"
__description__ = "Network diagnostics, MTU probing, Public IP discovery, HTTP/HTTPS internet connectivty tests, ping, name resolution..."
__licence__ = "BSD 3 Clause"
__version__ = "1.4.0"
__build__ = "2023093001"
__compat__ = "python2.7+"

import logging
import os
import socket
import warnings
from ipaddress import IPv4Address, IPv6Address, AddressValueError
import time
import psutil

from command_runner import command_runner
from requests import get
import requests.packages.urllib3.util.connection

from ofunctions import bisection
from ofunctions.threading import threaded
from ofunctions.misc import BytesConverter

# python 2.7 compat fixes
try:
    from typing import List, Tuple, Union, Iterable, Optional
except ImportError:
    pass

logger = logging.getLogger(__intname__)


def ping(
    targets=None,
    # type: Union[Iterable[Union[str, IPv4Address, IPv6Address]], Union[str, IPv4Address, IPv6Address]]
    mtu=1200,  # type: int
    retries=2,  # type: int
    timeout=4,  # type: float
    interval=1,  # type: float
    ip_type=None,  # type : int
    do_not_fragment=False,  # type: bool
    all_targets_must_succeed=False,  # type: bool
    source_interface=None,  # type : str
):
    # type: (...) -> bool
    """
    Tests if ICMP ping works
    IF all targets_must_succeed is False, at least one good result gives a positive result

    targets: can be a list of targets, or a single targets
    timeout: is in seconds
    interval: is in seconds seconds, linux only

    """

    icmp_overhead = 8 + 20
    mtu_encapsulated = mtu - icmp_overhead

    # Let's have a maximum process timeout for subprocess of 5 seconds extra ontop of the ping timeout
    # timeout is in seconds (int)
    command_timeout = int(timeout + 5)
    # windows uses timeout in milliseconds
    windows_timeout = timeout * 1000

    if mtu_encapsulated < 0:
        raise ValueError("MTU cannot be lower than {}.".format(icmp_overhead))

    if targets is None:
        # Cloudflare, Google and OpenDNS dns servers
        targets = ["1.1.1.1", "8.8.8.8", "208.67.222.222"]

    def _ping_host(target, retries, source_interface):
        if os.name == "nt":
            # -4/-6: IPType
            # -n ...: number of packets to send
            # -f: do not fragment
            # -l ...: packet size to send
            # -w ...: timeout (ms)
            # -S ...: optional source addr (IP) (which binds to source interface)
            command = "ping -n 1 -l {} -w {}".format(mtu_encapsulated, windows_timeout)

            # IPv6 does not allow to set fragmentation
            if do_not_fragment and ip_type != 6:
                command += " -f"
            encoding = "cp437"
        else:
            # -4/-6: IPType
            # -c ...: number of packets to send
            # -M do: do not fragment
            # -s ...: packet size to send
            # -i ...: interval (s), only root can set less than .2 seconds
            # -W ...: timeous (s)
            # -I ...: optional source interface name
            command = "ping -c 1 -s {} -W {} -i {}".format(
                mtu_encapsulated, timeout, interval
            )

            # IPv6 does not allow to set fragmentation
            if do_not_fragment and ip_type != 6:
                command += " -M do"
            encoding = "utf-8"

        # Add ip_type if specified
        if ip_type:
            command += " -{}".format(ip_type)

        if source_interface:
            # Try to detect what kind of source we're dealing with, IP address or interface name
            try:
                IPv6Address(source_interface)
                source_type = "ip"
            except ValueError:
                try:
                    IPv4Address(source_interface)
                    source_type = "ip"
                except ValueError:
                    source_type = "iface"

            if source_type == "ip":
                if os.name != "nt":
                    raise ValueError(
                        "Source address does only work on Windows platform"
                    )
                # -S
                command += " -S {}".format(source_interface)

            if source_type == "iface":
                if os.name == "nt":
                    raise ValueError(
                        "Source interface does not work on Windows platform"
                    )
                command += " -I {}".format(source_interface)

        command += " {}".format(target)
        result = False
        while retries > 0 and not result:
            exit_code, output = command_runner(
                command, timeout=command_timeout, encoding=encoding
            )
            if exit_code == 0:
                return True
            retries -= 1
        return False

    if all_targets_must_succeed:
        all_ping_results = True
    else:
        all_ping_results = False

    # Handle the case when a user gives a single target instead of a list
    for target in targets if isinstance(targets, list) else [targets]:
        if _ping_host(target, retries, source_interface):
            if not all_targets_must_succeed:
                all_ping_results = True
                break
        else:
            if all_targets_must_succeed:
                all_ping_results = False
                break

    return all_ping_results


def resolve_hostname(host):
    """
    Resolves a hostname
    """
    ip_list = []

    try:
        # Port is required
        # python 2.7 getaddrinfo does not take keyword arguments
        # for result in socket.getaddrinfo(host=host, port=0, type=socket.SOCK_STREAM):
        for result in socket.getaddrinfo(host, 0, socket.SOCK_STREAM):
            ip_list.append(str(result[4][0]))
    except socket.gaierror:
        logger.info('Cannot resolve hostname "{}"'.format(host))
    return ip_list


def proxy_dict(proxy):
    # type: (str) -> Optional[dict]
    """
    Transform a simple proxy URL into a dict
    """
    if proxy is not None:
        if proxy.startswith("http"):
            return {"http": proxy.strip("http://")}
        elif proxy.startswith("https"):
            return {"https": proxy.strip("https://")}
    return None


def _try_server(server, proxy_dict, timeout):
    # type: (str, dict, int) -> Tuple[bool, str]
    diag_messages = ""

    # With optional proxy
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=Warning)
            r = get(server, proxies=proxy_dict, verify=False, timeout=timeout)
        status_code = r.status_code
    except Exception as exc:
        diag_messages = "{0}\n{1}".format(diag_messages, str(exc))
        status_code = -1
    if status_code == 200:
        return (True, r.text)
    else:
        # Check without proxy (if set)
        if proxy_dict is not None:
            try:
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=Warning)
                    r = get(server, verify=False, timeout=timeout)
                status_code = r.status_code
            except Exception as exc:
                diag_messages = "{0}\n{1}".format(diag_messages, str(exc))
                status_code = -2
            if status_code == 200:
                return (True, r.text)
        diag_messages = "{0}\nCould not connect to [{1}], http error {2}.".format(
            diag_messages, server, status_code
        )
        return (False, diag_messages)


def test_http_internet(
    fqdn_servers=None,  # type: List[str]
    ip_servers=None,  # type: List[Union[IPv4Address, IPv6Address]]
    proxy=None,  # type: str
    timeout=5,  # type: int
    all_targets_must_succeed=False,  # type: bool
):
    # type: (...) -> bool
    """
    Tests if http(s) internet works
    At least one good result gives a positive result
    """
    if fqdn_servers is None:
        # Let's use some well known default servers
        fqdn_servers = [
            "http://www.google.com",
            "https://www.google.com",
            "http://kernel.org",
        ]
    if fqdn_servers is False:
        fqdn_servers = []
    if ip_servers is None:
        # Cloudflare dns servers respond to http requests, let's use them for ping checks
        ip_servers = ["http://1.1.1.1", "https://1.0.0.1"]
    if ip_servers is False:
        ip_servers = []

    diag_messages = ""

    if all_targets_must_succeed:
        fqdn_success = True
        ip_success = True
    else:
        fqdn_success = False
        ip_success = False
    dns_resolver_works = False

    for fqdn_server in fqdn_servers:
        result, diag = _try_server(fqdn_server, proxy_dict(proxy), timeout)
        diag_messages = diag_messages + diag
        if result:
            if not all_targets_must_succeed:
                fqdn_success = True
                break
        else:
            # Let's try to check whether DNS resolution works
            try:
                hostname = str(fqdn_server).split("//")[1]
            except IndexError:
                hostname = fqdn_server
            if resolve_hostname(hostname):
                dns_resolver_works = True
            if all_targets_must_succeed:
                fqdn_success = False
                break

    for ip_server in ip_servers:
        result, diag = _try_server(ip_server, proxy_dict(proxy), timeout)
        diag_messages = diag_messages + diag
        if result:
            if not all_targets_must_succeed:
                ip_success = True
                break
        else:
            if all_targets_must_succeed:
                ip_success = False
                break

    # Only ip servers succeed, but not fqdn servers
    if (not (fqdn_servers and fqdn_success)) and ip_success:
        # Don't bother with diag message when multiple fqdn_servers exist and all_targets_must_succeed is enabled
        if not all_targets_must_succeed or (
            all_targets_must_succeed and len(fqdn_servers) == 1
        ):
            diag_messages = (
                diag_messages
                + "\nNo FQDN server test worked, but at least one IP server test worked. "
                "Looks like a DNS resolving issue, or IP specific firewall rules."
            )
        if not dns_resolver_works:
            diag_messages = (
                diag_messages + "\nIt seems that DNS resolution does not work."
            )
        else:
            diag_messages = diag_messages + "\nDNS resolution seems to work."
        logger.info(diag_messages)
        return True

    # Neither fqdn servers nor ip_servers worked
    if not ((fqdn_servers and fqdn_success) or (ip_servers and ip_success)):
        logger.info(diag_messages)
        return False

    return True


def get_public_ip(check_services=None, proxy=None, timeout=5, ip_version: int = None):
    # type: (list, dict, int, int) -> Optional[int]
    """
    Get public IP address from one of the various web services
    """
    if check_services is None:
        check_services = [
            "https://ident.me",
            "http://ipinfo.io/ip",
            "http://ifconfig.me/ip",
            "https://ifconfig.me/ip",
            "http://api.ipify.org",
            "https://api.ipify.org",
        ]

    prior_ip_version = get_ip_version()

    if ip_version:
        set_ip_version(ip_version)
    for check_service in check_services:
        result, content = _try_server(
            check_service, proxy_dict=proxy_dict(proxy), timeout=timeout
        )
        if result:
            # We need to set ip version back to what it was
            set_ip_version(prior_ip_version)
            return content
    set_ip_version(prior_ip_version)
    return None


def get_public_hostname(ip=None):
    # type: (Optional[Union[IPv6Address, IPv6Address]]) -> Optional[str]
    """
    Get DNS record from public IP
    """
    if not ip:
        ip = get_public_ip()
    if ip:
        try:
            return socket.gethostbyaddr(ip)[0]
        except Exception:
            pass
    return None


def probe_mtu(target, method="ICMP", min=1100, max=9000, source_interface=None):
    # type: (Union[str, IPv4Address, IPv6Address], str, int, int, str) -> int
    """
    Detects MTU to target
    Probing can take up to 15-20 seconds

    MTU 65536 bytes is maxiumal value
    Standard values are
      1500 for ethernet over WAN
      1492 for ethernet over ADSL
      9000 for ethernet over LAN with jumbo frames
      13xx for ethernet over 3G/4G

    Optional source when using ICMP can be interface or IPaddress
    """

    if not target:
        raise ValueError("No valid target given.")

    if method == "ICMP":
        # Let's always keep 2 retries just to make sure we don't get false positives
        # timeout = 4, interval = 1, ip_type is detected
        ip_type = 4
        try:
            IPv6Address(target)
            ip_type = 6
        except AddressValueError:
            # Let's assume it's IPv4:
            pass

        ping_args = [
            (target, mtu, 2, 4, 1, ip_type, True, False, source_interface)
            for mtu in range(min, max + 1)
        ]

        # Bisect will return argument, list, let's just return the MTU
        try:
            return bisection.bisect(ping, ping_args, allow_all_expected=True)[1]
        except ValueError as exc:
            # Bisection failed, let's check if at least ping works to target
            result = ping(target, 28, 2, 4, 1, ip_type, False, False, source_interface)
            if not result:
                raise ValueError(
                    'ICMP request on target "{}" failed. Cannot determine MTU.'.format(
                        target
                    )
                )
            else:
                raise ValueError(
                    "Unable to determine MTU via defined method: {}".format(exc)
                )
    else:
        raise ValueError("Method {} not implemented yet.".format(method))


class IOInterface:
    """
    IOCounters counts instant sent / received bytes as soon a class instance is created
    Also counts total and average send / received bytes
    """

    def __init__(self, name):
        self.name = name
        self._sent = BytesConverter(0)
        self._recv = BytesConverter(0)
        self._sent_total = BytesConverter(0)
        self._recv_total = BytesConverter(0)
        self._sent_avg_speed = BytesConverter(0)  # b/s
        self._recv_avg_speed = BytesConverter(0)  # b/s

        # Everytime we set sent/recv bytes with a new value, we'll increase the number of samples so we get to calculate average speed
        self._sent_avg_speed_samples = 0
        self._recv_avg_speed_samples = 0

        # We may also reset total counters by keeping before reset value here
        self._sent_total_reset_value = 0
        self._recv_total_reset_value = 0

    def __repr__(self):
        return "Interface {}: {} sent bytes, {} recv bytes, {} total sent bytes, {} total recv bytes, Avg {} bytes/s sent, Avg {} bytes/s recv".format(
            self.name,
            self.sent,
            self.recv,
            self.sent_total,
            self.recv_total,
            self._sent_avg_speed,
            self._recv_avg_speed,
        )

    @property
    def sent(self):
        return self._sent

    @sent.setter
    def sent(self, value):
        # type: (int) -> None
        self._sent = BytesConverter(value)

    @property
    def recv(self):
        return self._recv

    @recv.setter
    def recv(self, value):
        # type: (int) -> None
        self._recv = BytesConverter(value)

    @property
    def sent_total(self):
        return self._sent_total

    @sent_total.setter
    def sent_total(self, value):
        # type: (int) -> None
        self._sent_total = BytesConverter(value - self._sent_total_reset_value)

    @property
    def recv_total(self):
        return self._recv_total

    @recv_total.setter
    def recv_total(self, value):
        # type: (int) -> None
        self._recv_total = BytesConverter(value - self._recv_total_reset_value)

    @property
    def sent_avg_speed(self):
        return self._sent_avg_speed

    @sent_avg_speed.setter
    def sent_avg_speed(self, value):
        # type: (int) -> None
        self._sent_avg_speed = BytesConverter(value)
        self._sent_avg_speed_samples += 1

    @property
    def sent_avg_speed_samples(self):
        return self._sent_avg_speed_samples

    @property
    def recv_avg_speed(self):
        return self._recv_avg_speed

    @recv_avg_speed.setter
    def recv_avg_speed(self, value):
        # type: (int) -> None
        self._recv_avg_speed = BytesConverter(value)
        self._recv_avg_speed_samples += 1

    @property
    def recv_avg_speed_samples(self):
        return self._recv_avg_speed_samples


class IOCounters:
    """ """

    def __init__(self, interface_names=None, resolution=1):
        # type: (List[str], float) -> None
        self.counters = {}
        self.stats = {}
        self.resolution = float(resolution)
        self.interfaces = {}
        self.interface_names = interface_names
        self._get_interface_names()

        # init each interface with a IOInterface counter class
        for interface in self.interface_names:
            self.interfaces[interface] = IOInterface(interface)

        # Start counters
        self._increase_counters()

    def _get_interface_names(self):
        """
        Get interfaces names if none given
        """
        if not self.interface_names:
            self.interface_names = []
            for interface in psutil.net_io_counters(pernic=True, nowrap=True):
                self.interface_names.append(interface)

    @threaded
    def _increase_counters(self):
        # Initialize total counters so we don't get high instant values at first run
        iface_results = psutil.net_io_counters(pernic=True, nowrap=True)
        for interface in self.interfaces:
            self.interfaces[interface]._sent_total_reset_value = BytesConverter(
                iface_results[interface].bytes_sent
            )
            self.interfaces[interface]._recv_total_reset_value = BytesConverter(
                iface_results[interface].bytes_recv
            )
            self.interfaces[interface].sent_total = BytesConverter(
                iface_results[interface].bytes_sent
            )
            self.interfaces[interface].recv_total = BytesConverter(
                iface_results[interface].bytes_recv
            )
        while True:
            iface_results = psutil.net_io_counters(pernic=True, nowrap=True)
            for interface in self.interfaces:
                sent_new_value = iface_results[interface].bytes_sent
                recv_new_value = iface_results[interface].bytes_recv
                # We still use BytesConverter cast here since Python 2.7 does not work when casting in IOInterface class property
                self.interfaces[interface].sent = BytesConverter(
                    sent_new_value
                    - self.interfaces[interface].sent_total
                    - self.interfaces[interface]._sent_total_reset_value
                )
                self.interfaces[interface].recv = BytesConverter(
                    recv_new_value
                    - self.interfaces[interface].recv_total
                    - self.interfaces[interface]._recv_total_reset_value
                )

                # Calculate average speed depending on self.resolution which is calculated in seconds
                sent_bytes_per_second = (
                    self.interfaces[interface].sent / self.resolution
                )
                self.interfaces[interface].sent_avg_speed = BytesConverter(
                    round(
                        (
                            self.interfaces[interface].sent_avg_speed
                            + sent_bytes_per_second
                        )
                        / (self.interfaces[interface].sent_avg_speed_samples + 1),
                        2,
                    )
                )
                recv_bytes_per_second = (
                    self.interfaces[interface].recv / self.resolution
                )
                self.interfaces[interface].recv_avg_speed = BytesConverter(
                    round(
                        (
                            self.interfaces[interface].recv_avg_speed
                            + recv_bytes_per_second
                        )
                        / (self.interfaces[interface].recv_avg_speed_samples + 1),
                        2,
                    )
                )
                self.interfaces[interface].sent_total = BytesConverter(sent_new_value)
                self.interfaces[interface].recv_total = BytesConverter(recv_new_value)
            time.sleep(self.resolution)

    def reset(self):
        iface_results = psutil.net_io_counters(pernic=True, nowrap=True)
        for interface in self.interfaces:
            self.interfaces[interface]._sent_total_reset_value = BytesConverter(
                iface_results[interface].bytes_sent
            )
            self.interfaces[interface]._recv_total_reset_value = BytesConverter(
                iface_results[interface].bytes_recv
            )
            self.interfaces[interface].sent_total = BytesConverter(
                iface_results[interface].bytes_sent
            )
            self.interfaces[interface].recv_total = BytesConverter(
                iface_results[interface].bytes_recv
            )
            self.interfaces[interface].sent_avg_speed = BytesConverter(0)
            self.interfaces[interface]._sent_avg_speed_samples = 0
            self.interfaces[interface].recv_avg_speed = BytesConverter(0)
            self.interfaces[interface]._recv_avg_speed_samples = 0


def get_ip_version():
    # type: () -> Optional[int]
    # pylint: disable=E1101 (no-member)
    ip_version = requests.packages.urllib3.util.connection.allowed_gai_family()
    if ip_version == socket.AF_INET6:
        return 6
    elif ip_version == socket.AF_INET:
        return 4
    else:
        return None


def set_ip_version(ip_version: int = 6):
    # type: (str) -> bool
    """
    Sets preferred IP protocol version to use in requests / ofunctions
    Attention: this propagates
    By default, AF_INET6 is used which preferes IPv6 but fallbacks to IPv4
    """
    if ip_version == 4:

        def allowed_gai_family():
            return socket.AF_INET

    elif ip_version == 6:

        def allowed_gai_family():
            # pylint: disable=E1101 (no-member)
            if requests.packages.urllib3.util.connection.HAS_IPV6:
                return socket.AF_INET6
            return socket.AF_INET

    else:
        return False

    # pylint: disable=E1101 (no-member)
    requests.packages.urllib3.util.connection.allowed_gai_family = allowed_gai_family
    return True
