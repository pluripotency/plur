import sys
import getpass as gpass
import pexpect

child_send = 'send'
child_sendline = 'sendline'
child_sendcontrol = 'sendcontrol'

waitprompt = 'waitprompt'
changeprompt = 'changeprompt'
Exit = 'exit'

def update_outputs(session, outputs):
    updated = []
    for op in outputs:
        if op[1] == p_capture:
            op[0] = session.waitprompt
        elif op[1] == waitprompt:
            op[1] = success
            if op[0] in [None, '']:
                op[0] = session.waitprompt

        elif op[1] == "timeout":
            op[0] = pexpect.TIMEOUT
            if len(op) > 2:
                op[1] = success_f(op[2])
            else:
                op[1] = success_f("timeout")

        elif op[1] == "EOF":
            op[0] = pexpect.EOF
            if len(op) > 2:
                op[1] = success_f(op[2])
            else:
                op[1] = success_f("EOF")
        updated += [op]
    return updated

def handle_output(session, outputs):
    """Decides reaction and returns result after success.
    :param outputs: expected output list
    :param timeout: timeout to get output from pty
    """

    updated = update_outputs(session, outputs)
    exout = [out[0] for out in updated]
    session.logger.debug_log.before_select(session, output_list=updated)
    while True:
        i = session.child.expect(exout)
        session.logger.debug_log.after_select(session, i)

        output = updated[i]

        reaction = output[1]
        if reaction in break_reactions:
            return reaction(session, output)
        if reaction in continue_reactions:
            reaction(session, output)
        elif reaction == 'exit':
            sys.exit(1)
        else:
            res = reaction(session)
            if res == 'p_continue':
                # continue
                pass
            else:
                return res

def wait(expect_list, pre_func=None):
    def run_in_wait(session):
        session.logger.message('in wait function')
        if callable(pre_func):
            pre_func(session)
        result = handle_output(session, expect_list)
        session.logger.message('out wait function')
        return result
    return run_in_wait

def success_f(value=None):
    def func(session):
        session.logger.debug_log.at_row_method(f'success_f returns: {value}')
        return value
    return func

def send_f(value=''):
    def func(session):
        session.child.send(value)
        session.logger.debug_log.at_row_method(f'send_f sent: {value}')
        return 'p_continue'
    return func

def send_line_f(value=''):
    def func(session):
        session.child.sendline(value)
        session.logger.debug_log.at_row_method(f'send_line_f sent: {value}')
        return 'p_continue'
    return func

def send_pass_f(value=''):
    def func(session):
        # disarm logging to avoid to log password.
        session.child.logfile = None
        session.logger.output_log.pause_output()

        if value != '':
            gp = value
        elif hasattr(session.nodes[-1], 'password'):
            gp = session.nodes[-1].password
        else:
            #Get password from command line.
            gp = gpass.getpass("")

        #send password
        session.child.sendline(gp)

        # continue logging.
        session.child.logfile = session.logger.output_log.continue_output()
        session.logger.debug_log.at_row_method('send_pass_f sent: (password omit)')
        return 'p_continue'
    return func

def send_control_f(value):
    def func(session):
        session.child.sendcontrol(value)
        session.logger.debug_log.at_row_method(f'send_control_f sent: Ctrl-{value}')
        return 'p_continue'
    return func

new_success = success_f
new_send = send_f
new_send_line = send_line_f
new_send_pass = send_pass_f
new_send_control = send_control_f

def p_capture(session, output):
    session.logger.debug_log.at_row_method('p_capture returns: child.before')
    return session.child.before

def success(session, output):
    res = False
    if len(output) > 2:
        res = output[2]
    session.logger.debug_log.at_row_method(f'success returns: {res}')
    return res

def expect(session, output):
    session.child.expect(output[2] + '\r')
    result = '\n matched: ' + session.child.after
    return result

def send(session, output):
    value = output[2]
    session.child.send(value)
    session.logger.debug_log.at_row_method(f'send sent: {value}')

def send_line(session, output):
    value = output[2]
    session.child.sendline(value)
    session.logger.debug_log.at_row_method(f'send_line sent: {value}')

def send_control(session, output):
    value = output[2]
    session.child.sendcontrol(value)
    session.logger.debug_log.at_row_method(f'send_control sent: Ctrl-{value}')

def send_pass(session, output):
    # disarm logging to avoid to log password.
    session.child.logfile = None
    session.logger.output_log.pause_output()

    if output is not None and len(output) > 2 and output[2] is not None:
        gp = output[2]
    elif hasattr(session.nodes[-1], 'password'):
        gp = session.nodes[-1].password
    else:
        #Get password from command line.
        gp = gpass.getpass("")

    #send password
    session.child.sendline(gp)

    # continue logging.
    session.child.logfile = session.logger.output_log.continue_output()
    session.logger.debug_log.at_row_method('send_pass sent: (password omit)')

def get_pass(session, output):
    # disarm logging to avoid to log password.
    session.child.logfile = None
    session.logger.output_log.pause_output()

    #Get password from command line.
    gp = gpass.getpass("")

    session.child.sendline(gp)

    # continue logging.
    session.child.logfile = session.logger.output_log.continue_output()
    session.logger.debug_log.at_row_method('get_pass sent: (password omit)')
    return gp

break_reactions = [success, expect, p_capture]
continue_reactions = [send, send_line, send_control, send_pass, get_pass]
