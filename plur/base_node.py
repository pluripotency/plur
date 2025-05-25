import inspect
import os
import re
import getpass
from mini import misc

# for reference only
class Host:
    def __init__(self):
        self.hostname = 'test'                   # needed
        self.username = 'root'                   # needed
        self.password = 'password'               # option
        self.platform = 'almalinux8'                # needed
        self.waitprompt = r'\[?root@test .+[$#]'  # needed

class Node:
    def __init__(self, dictionary):
        self.__dict__ = dictionary

def is_platform_rhel(platform):
    return bool(re.search('centos|fedora|rhel|alma|rocky', platform))

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

class SuNode:
    def __init__(self, current_node, username='root'):
        self.set_str_attr(current_node)
        self.username = username
        self.waitprompt = get_linux_waitprompt(current_node.platform, current_node.hostname, username)

    def set_str_attr(self, node):
        for k, v in [mem for mem in inspect.getmembers(node) if isinstance(mem[1], str)]:
            setattr(self, k, v)

class Linux:
    def __init__(self, hostname, username='worker', password='password', platform='almalinux8'):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.platform = platform
        self.waitprompt = get_linux_waitprompt(platform, hostname, username)

class Me:
    def __init__(self, platform=None):
        if not platform:
            redhat_release_path = '/etc/redhat-release'
            etc_issue_path = '/etc/issue'
            if misc.is_file(redhat_release_path):
                redhat_dist = misc.open_read(redhat_release_path)
                if re.search('AlmaLinux release 9', redhat_dist):
                    platform = 'almalinux9'
                elif re.search('AlmaLinux release 8', redhat_dist):
                    platform = 'almalinux8'
                elif re.search('CentOS Linux release 7', redhat_dist):
                    platform = 'centos7'
                elif re.search('CentOS Linux release 6', redhat_dist):
                    platform = 'centos6'
                else:
                    platform = 'almalinux8'
            elif misc.is_file(etc_issue_path):
                etc_issue = misc.open_read(etc_issue_path)
                if re.search('Ubuntu 22.04', etc_issue):
                    platform = 'ubuntu jammy'
                elif re.search('Ubuntu', etc_issue):
                    platform = 'ubuntu'
                elif re.search('Arch Linux', etc_issue):
                    platform = 'arch'
            if not platform:
                platform = 'almalinux9'

        hostname = os.uname()[1].split(".")[0]
        username = getpass.getuser()
        self.hostname = hostname
        self.username = username
        self.password = ''
        self.platform = platform
        self.waitprompt = get_linux_waitprompt(platform, hostname, username)

class LeastMe:
    def __init__(self):
        self.hostname = os.uname()[1].split(".")[0]
        self.username = getpass.getuser()
        self.waitprompt = '[#$%] '
