from mini.ansi_colors import cyan,red
from plur import session_wrap
from plur import base_shell


def sample():
    @session_wrap.bash()
    def func(session):
        ping_target = '127.0.0.1'
        ping_result = base_shell.is_ping_ok(ping_target)(session)
        if ping_result:
            print(cyan(f'Ping Success: {ping_target}'))
        else:
            print(red(f'Ping Failed: {ping_target}'))
        return ping_result
    return func()
