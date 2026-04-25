import re
from typing import Annotated
from pydantic.functional_validators import AfterValidator
from mini import misc

def check_ipv4(v: str) -> str:
    assert misc.is_ipv4(v), f"invalid ipv4 format: {v}"
    return v

ValidIpv4 = Annotated[str, AfterValidator(check_ipv4)]

def check_ipv4_list(v_list: list) -> list:
    for v in v_list:
        assert misc.is_ipv4(v), f"invalid ipv4 format: {v}"
    return v_list

ValidIpv4List = Annotated[list, AfterValidator(check_ipv4_list)]

def check_ipv4_with_prefix(v: str) -> str:
    assert misc.is_ipv4_with_prefix(v), f"invalid ipv4 with prefix format: {v}"
    return v

ValidIpv4WithPrefix = Annotated[str, AfterValidator(check_ipv4_with_prefix)]

def check_ipv4_route_list(v: str) -> str:
    assert misc.is_ipv4_route_list(v), f"invalid ipv4 route list format: {v}"
    return v

ValidIpv4RouteList = Annotated[str, AfterValidator(check_ipv4_route_list)]

def is_platform_rhel(platform):
    return bool(re.search('centos|fedora|rhel|alma|rocky', platform))

def check_platform_rhel(platform):
    assert is_platform_rhel(platform)
    return platform

ValidRHELPlatform = Annotated[str, AfterValidator(check_platform_rhel)]

def is_platform_systemd(platform):
    return not bool(re.search('centos6', platform))

def _user_linux_waitprompt(platform, hostname, username):
    if is_platform_rhel(platform):
        return rf'\[?{username}@{hostname} .+\]\$ '
    return rf'{username}@{hostname}..+\$ '

def _root_linux_waitprompt(platform, hostname):
    if is_platform_rhel(platform):
        return rf'\[?root@{hostname} .+\]# '
    return rf'root@{hostname}..+# '

def get_linux_waitprompt(platform, hostname, username='root'):
    if username == 'root':
        return _root_linux_waitprompt(platform, hostname)
    return _user_linux_waitprompt(platform, hostname, username)


