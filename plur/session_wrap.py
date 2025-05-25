import sys
from mini import ansi_colors
from plur.session import Session
from plur import base_node
from plur import base_shell

def run_session(node, login_method=None, log_params=None, custom_method=None):
    def receive_func(func):
        def run(session=None):
            if session is None:
                single_hierarchy = True
                session = Session(node, log_params=log_params)
            else:
                single_hierarchy = False
                session.push_node(node)

            if custom_method and callable(custom_method):
                custom_method(session)
            else:
                if login_method and hasattr(session, login_method):
                    method = getattr(session, login_method)
                    method()
                else:
                    print(ansi_colors.red(f'err in run_session: unknown login_method: {login_method}'))
                    sys.exit(1)

            result = func(session)

            current_node = session.nodes[-1]
            if hasattr(node, 'exit_session') and callable(node.exit_session):
                node.exit_session(session)
            else:
                exit_command = current_node.exit_command if hasattr(current_node, 'exit_command') else 'exit'
                if single_hierarchy:
                    rows = [['', 'EOF', None]]
                    session.do(base_shell.create_sequence(exit_command, rows))
                else:
                    session.pop_node()
                    session.run(exit_command)

            if single_hierarchy:
                session.close()
            return result

        return run

    return receive_func

def telnet(node, log_params=None):
    return run_session(node, 'telnet', log_params)

def ssh(node, log_params=None):
    return run_session(node, 'ssh', log_params)

def bash(node=None, log_params=None):
    if node is None:
        node = base_node.Me()
    return run_session(node, 'bash', log_params)

def sudo(func):
    def run(session):
        sudo_on = False
        if session.nodes[-1].username != 'root':
            sudo_on = True
            session.sudo_i()
        result = func(session)
        if sudo_on:
            session.su_exit()
        return result
    return run

def su(username='root'):
    def receive_func(func):
        def run(session):
            su_on = False
            if session.nodes[-1].username != username:
                su_on = True
                session.su(username)
            result = func(session)
            if su_on:
                session.su_exit()
            return result
        return run
    return receive_func
