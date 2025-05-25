import sys
from mini import ansi_colors
from plur import base_node
from plur import session_wrap

def extract_ssh_node_from_dict(hostname, username, password, access_ip, platform='almalinux8', **kwargs):
    node = base_node.Linux(hostname, username, password, platform)
    node.access_ip = access_ip
    return node

def extract_bash_node_from_dict(hostname, username, platform='almalinux8', **kwargs):
    node = base_node.Linux(hostname, username, '', platform)
    return node

def by_node_dict(node_dict, log_params=None, login_method=None):
    if 'login_method' in node_dict:
        login_method = node_dict['login_method']
    elif not login_method:
        login_method = 'ssh'
    if login_method in ['ssh', 'telnet']:
        node = extract_ssh_node_from_dict(**node_dict)
    elif login_method == 'bash':
        node = extract_bash_node_from_dict(**node_dict)
    else:
        print(ansi_colors.red(f'err in by_node_dict: unknown login_method: {login_method}'))
        sys.exit(1)
    return session_wrap.run_session(node, login_method, log_params)

def telnet(node_dict, log_params=None):
    return by_node_dict(node_dict, log_params, 'telnet')

def ssh(node_dict, log_params=None):
    return by_node_dict(node_dict, log_params)

def bash(node_dict=None, log_params=None):
    if node_dict is None:
        return session_wrap.run_session(base_node.Me(), 'bash', log_params)
    return by_node_dict(node_dict, log_params, 'bash')

def sudo(func):
    return session_wrap.sudo(func)

def su(username='root'):
    return session_wrap.su(username)
