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
__copyright__ = "Copyright (C) 2014-2021 Orsiris de Jong"
__description__ = "Network diagnostics, MTU probing, Public IP discovery, HTTP/HTTPS internet connectivty tests, ping, name resolution..."
__licence__ = "BSD 3 Clause"
__version__ = "1.0.1"
__build__ = "2021122201"

import os
from ofunctions import bisection
from typing import List, Tuple, Union, Iterable, Optional
from ipaddress import IPv6Address, AddressValueError
from command_runner import command_runner
from requests import get
import socket
import warnings
import logging

logger = logging.getLogger()


def ping(
    targets: Union[Iterable[str], str] = None,
    mtu: int = 1200,
    retries: int = 2,
    timeout: float = 4,
    interval: float = 1,
    ip_type: int = None,
    do_not_fragment: bool = False,
    all_targets_must_succeed: bool = False,
) -> bool:
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

    def _try_server(target):
        nonlocal retries

        if os.name == "nt":
            # -4/-6: IPType
            # -n ...: number of packets to send
            # -f: do not fragment
            # -l ...: packet size to send
            # -w ...: timeout (ms)
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
        if _try_server(target):
            if not all_targets_must_succeed:
                all_ping_results = True
                break
        else:
            if all_targets_must_succeed:
                all_ping_results = False
                break

    return all_ping_results


def resolve_hostname(host: str) -> Optional[list]:
    """
    Resolves a hostname
    """
    ip_list = []

    try:
        # Port is required
        for result in socket.getaddrinfo(host=host, port=0, type=socket.SOCK_STREAM):
            ip_list.append(str(result[4][0]))
    except socket.gaierror:
        logger.info('Cannot resolve hostname "{}"'.format(host))
    return ip_list


def proxy_dict(proxy: str) -> Union[dict, None]:
    if proxy is not None:
        if proxy.startswith("http"):
            return {"http": proxy.strip("http://")}
        elif proxy.startswith("https"):
            return {"https": proxy.strip("https://")}
    return None


def test_http_internet(
    fqdn_servers: List[str] = None,
    ip_servers: List[str] = None,
    proxy: str = None,
    timeout: int = 5,
    all_targets_must_succeed: bool = False,
) -> bool:
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

    def _try_server(server: str, proxy_dict: dict) -> Tuple[bool, str]:
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
            return True, diag_messages
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
                    # diag_messages = diag_messages + f'\nCould connect to [{server}].'
                    return True, diag_messages
            diag_messages = "{0}\nCould not connect to [{1}], http error {2}.".format(
                diag_messages, server, status_code
            )
            return False, diag_messages

    if all_targets_must_succeed:
        fqdn_success = True
        ip_success = True
    else:
        fqdn_success = False
        ip_success = False
    dns_resolver_works = False

    for fqdn_server in fqdn_servers:
        result, diag = _try_server(fqdn_server, proxy_dict(proxy))
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
        result, diag = _try_server(ip_server, proxy_dict(proxy))
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


def get_public_ip(
    check_services=None, proxy: str = None, timeout: int = 5
) -> Optional[str]:
    """
    Get public IP address from one of the various web services
    """
    if check_services is None:
        check_services = [
            "https://ident.me",
            "https://api.ipify.org",
            "http://ipinfo.io/ip",
            "http://ifconfig.me/ip",
        ]

    def _try_server(server: str, proxy_dict: dict) -> Optional[str]:
        # With optional proxy
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=Warning)
                r = get(server, proxies=proxy_dict, verify=False, timeout=timeout)
            status_code = r.status_code
        except Exception as exc:
            status_code = -1
        if status_code == 200:
            return r.text
        else:
            # Check without proxy (if set)
            if proxy_dict is not None:
                try:
                    with warnings.catch_warnings():
                        warnings.filterwarnings("ignore", category=Warning)
                        r = get(server, verify=False, timeout=timeout)
                    status_code = r.status_code
                except Exception as exc:
                    status_code = -2
                if status_code == 200:
                    return r.text
        return None

    for check_service in check_services:
        result = _try_server(check_service, proxy_dict=proxy_dict(proxy))
        if result:
            return result


def probe_mtu(target: str, method: str = "ICMP", min: int = 1100, max: int = 9000):
    """
    Detects MTU to target
    Probing can take up to 15-20 seconds

    MTU 65536 bytes is maxiumal value
    Standard values are
      1500 for ethernet over WAN
      1492 for ethernet over ADSL
      9000 for ethernet over LAN with jumbo frames
      13xx for ethernet over 3G/4G
    """

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
            (target, mtu, 2, 4, 1, ip_type, True) for mtu in range(min, max + 1)
        ]

        # Bisect will return argument, list, let's just return the MTU
        try:
            return bisection.bisect(ping, ping_args, allow_all_expected=True)[1]
        except ValueError as exc:
            # Bisection failed, let's check if at least ping works to target
            result = ping(target, 28, 2, 4, 1, ip_type)
            if not result:
                raise OSError(
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
