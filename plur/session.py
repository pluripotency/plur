import sys
from mini.ansi_colors import red
from plur import base_shell
from plur.spawn import Spawn


class Session(Spawn):
    def __init__(self, node, log_params=None):
        self.push_node(node)
        Spawn.__init__(self, log_params)

    def run(self, action):
        return base_shell.run(self, action)

    def add_attrs(self, src_obj, attrs):
        for attr in attrs:
            if hasattr(src_obj, attr):
                setattr(self, attr, getattr(src_obj, attr))

    def push_node(self, node):
        if hasattr(self, 'nodes'):
            self.nodes.append(node)
        else:
            self.nodes = [node]
        self.add_attrs(node, ['hostname', 'username', 'platform', 'waitprompt'])

    def pop_node(self):
        if len(self.nodes) > 1:
            self.nodes.pop()
        node = self.nodes[-1]
        self.add_attrs(node, ['hostname', 'username', 'platform', 'waitprompt'])

    def ssh(self):
        base_shell.ssh_session(self)
        return self

    def telnet(self):
        base_shell.telnet_session(self)
        return self

    def bash(self):
        base_shell.bash_session(self)
        return self

    def su(self, user='root'):
        if base_shell.su(self, user=user):
            return self
        # force exit
        self.logger.debug_log.message(red('failed to session.su, exiting'))
        sys.exit(1)

    def sudo_i(self):
        if base_shell.sudo_i(self):
            return self
        # force exit
        self.logger.debug_log.message(red('failed to session.sudo_I, exiting'))
        sys.exit(1)

    def su_exit(self):
        self.pop_node()
        base_shell.run(self, 'exit')
        return self

