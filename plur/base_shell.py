import sys
import re
from mini import ansi_colors
from plur import base_node
from plur import output_methods

def create_sequence(action, rows, method_type=None):
    """
    >>> create_sequence('action', [['', output_methods.waitprompt, True, '']])
    [['action', [['', 'waitprompt', 'y', 'waiting for prompt']], child_sendline]]
    :param action: commandt to send to pty
    :param rows: command responses expected
    :param method_type: child_sendline is default, child_sendcontrol can be selected.
    """
    return [action, rows, method_type]

def run(session, command):
    return session.do(create_sequence(command, [['', output_methods.p_capture, '', command]]))

def capture_by_file_writer(file_path, write_mode='w'):
    def receive_func(received_func):
        def run_func(session):
            session.logger.output_log.add_file_writer(file_path, write_mode)
            result = received_func(session)
            session.logger.output_log.pause_output()
            session.child.logfile = session.logger.output_log.continue_output()
            return result
        return run_func
    return receive_func

def command_capture_by_file_writer(command, file_path, write_mode='w'):
    return capture_by_file_writer(file_path, write_mode)(lambda session: run(session, command))

def find_platform(session):
    redhat_release_path = '/etc/redhat-release'
    if check_file_exists(session, redhat_release_path):
        capt = run(session, f'cat {redhat_release_path}')
        for line in re.split('\r?\n', ansi_colors.rm_color(capt)):
            if line.startswith('AlmaLinux release 9'):
                return 'almalinux9'
            if line.startswith('AlmaLinux release 8'):
                return 'almalinux8'
            if line.startswith('CentOS Linux release 7'):
                return 'centos7'
    else:
        etc_issue_path = '/etc/issue'
        if check_file_exists(session, etc_issue_path):
            capt = run(session, f'cat {etc_issue_path}')
            for line in re.split('\r?\n', ansi_colors.rm_color(capt)):
                if line.startswith('Ubuntu'):
                    if re.search('22.04', line):
                        return 'ubuntu jammy'
                    if re.search('24.04', line):
                        return 'ubuntu noble'
                    return 'ubuntu'
    return False

def telnet(session, hostname_or_ip, username):
    action = f'telnet {hostname_or_ip}'
    rows = expects_on_login()
    rows.append(['login:', output_methods.send_line, username, 'waiting for user input'])
    session.do(create_sequence(action, rows))

def ssh(session, hostname_or_ip, login_name=None, port=22, other_options=None):
    action = 'ssh ' + hostname_or_ip
    if login_name is not None:
        action += ' -l ' + login_name
    if port != 22 and isinstance(port, int) and port < 65536:
        action += ' -p ' + str(port)
    if other_options is not None:
        action += ' ' + other_options
    session.do(create_sequence(action, expects_on_login()))

def get_access_target(node):
    access_target = None
    for at in ['access_ip', 'hostname']:
        if hasattr(node, at):
            access_target = getattr(node, at)
            break
    if access_target is None:
        print(ansi_colors.red('err in get_access_target: access_ip, hostname is needed.'))
        sys.exit(1)
    return access_target

# def set_session_hostname(session):
#     hostname = None
#     capt = run(session, 'echo HOSTNAME:$HOSTNAME')
#     for line in re.split('\r\n|\n', capt):
#         if re.match('HOSTNAME:', line):
#             hostname = line.split(':')[1].split('.')[0]
#     if hostname is not None:
#         session.nodes[-1].hostname = hostname
#         session.hostname = hostname
#
#
# def set_session_platform(session):
#     platform = None
#     # if Linux
#     redhat_release = '/etc/redhat-release'
#     etc_issue = '/etc/issue'
#     if check_file_exists(session, redhat_release):
#         captured = run(session, 'cat ' + redhat_release)
#         if re.search('CentOS Linux release 7', captured):
#             platform = 'centos7'
#         elif re.search('CentOS release 6', captured):
#             platform = 'centos6'
#     elif check_file_exists(session, etc_issue):
#         captured = run(session, 'cat ' + etc_issue)
#         if re.search('Ubuntu', captured):
#             platform = 'ubuntu'
#
#     if platform is not None:
#         session.nodes[-1].platform = platform
#         session.platform = platform
#
#
# def set_session_waitprompt(session):
#     import datetime
#     now = datetime.datetime.now().strftime('%H%M%S_%f')
#     this_waitprompt = '%s:> ' % now
#
#     session.nodes[-1].waitprompt = this_waitprompt
#     session.waitprompt = this_waitprompt
#     run(session, 'export PS1="%s"' % this_waitprompt)

def lang_c(session):
    # run(session, 'export LANG=C.UTF-8 TERM=dummy PROMPT_COMMAND=""')
    run(session, 'stty -echo')
    run(session, 'export LANG=C PROMPT_COMMAND=""')
    # run(session, 'export PROMPT_COMMAND="printf PLUR:"')
    # run(session, 'export LANG=C')
    # set_session_hostname(session)
    # set_session_platform(session)
    # set_session_waitprompt(session)

def platform_run(session):
    node = session.nodes[-1]
    if hasattr(node, 'platform'):
        platform = getattr(node, 'platform')
        if platform in ['almalinux8', 'almalinux9', 'centos8', 'centos9']:
            lang_c(session)
            run(session, "bind 'set enable-bracketed-paste off'")
        elif re.search('centos|rhel|fedora|ubuntu', platform):
            lang_c(session)

def ssh_session(session):
    node = session.nodes[-1]
    node.exit_command = 'exit'

    access_target = get_access_target(node)

    username = node.username if hasattr(node, 'username') else None
    if username is None:
        print(ansi_colors.red('err in ssh_session: node.username is needed.'))
        sys.exit(1)

    action = f'ssh {username}@{access_target}'
    action += f' -p {node.ssh_port}' if hasattr(node, 'ssh_port') else ''
    action += f' {node.ssh_options}' if hasattr(node, 'ssh_options') else ''

    session.do(create_sequence(action, expects_on_login()))
    platform_run(session)

def telnet_session(session):
    node = session.nodes[-1]
    node.exit_command = 'exit'

    access_target = get_access_target(node)

    action = f'telnet {access_target}'
    username = node.username if hasattr(node, 'username') else None
    if username is None:
        print(ansi_colors.red('err in telnet_session: node.username is needed.'))
        sys.exit(1)

    rows = expects_on_login()
    rows.append(['[Ll]ogin:', output_methods.send_line, username, 'waiting for user input'])
    session.do(create_sequence(action, rows))
    platform_run(session)

def bash_session(session):
    node = session.nodes[-1]
    node.exit_command = 'exit'
    run(session, 'bash')
    platform_run(session)

def expects_on_login(password=''):
    rows = [
        [r'Are you sure you want to continue connecting \(yes/no.+\?', output_methods.send_line, 'yes'],
        ["[Pp]assword:", output_methods.new_send_pass(password), None],
        ["Permission denied, please try again.+password:", output_methods.get_pass, None],
        [r"Permission denied \(publickey,", 'exit', ''],
        ["WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!", 'exit', ''],
        ["ssh: Could not resolve hostname", 'exit', ''],
        ["ssh: connect to host ", 'exit', ''],
        ['', output_methods.p_capture, '']
    ]
    return [row + [row[0]] for row in rows]

# def id(session, user):
#     result = session.do('id ' + user, [
#         ['uid=', output_methods.success, True],
#         ['id: %s: no such user' % user, output_methods.success, False]
#     ])
#     session.child.expect(session.nodes[-1].waitprompt)
#     return result

def find_root_password_from_nodes(session):
    for node in session.nodes:
        if hasattr(node, 'root_password'):
            return node.root_password
        if node.username == 'root' and hasattr(node, 'password'):
            return node.password
    return False

def su(session, user='root'):
    current_node = session.nodes[-1]
    current_user = current_node.username
    if current_user == user:
        # avoid excess nodes hierarchy
        return True
    su_node = base_node.SuNode(current_node, user)
    rows = [
        [su_node.waitprompt, output_methods.success, True],
        [current_node.waitprompt, output_methods.success, False]
    ]
    if current_user == 'root':
        result = session.do(create_sequence('su - ' + user, rows))
        if result is True:
            session.push_node(su_node)
            platform_run(session)
        return result
    if user is None or user == 'root':
        action = 'su -'
    else:
        action = 'su - ' + user
    found_root_password = find_root_password_from_nodes(session)
    if found_root_password:
        rows += [
            ["[Pp]assword:", output_methods.new_send_pass(found_root_password), None],
        ]
    else:
        rows += [
            ["[Pp]assword:", output_methods.get_pass, None],
        ]
    result = session.do(create_sequence(action, rows))
    if result is True:
        session.push_node(su_node)
        platform_run(session)
    return result

def add_sudoer(session, username):
    current_node = session.nodes[-1]
    current_username = current_node.username
    if current_username == 'root':
        run(session, f'echo "{username} ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/{username}')
        return True
    su(session)
    add_sudoer(session, username)
    session.pop_node()
    run(session, 'exit')
    return False

def sudo_i_password(session):
    current_node = session.nodes[-1]
    su_node = base_node.SuNode(current_node, 'root')

    rows = [
        [su_node.waitprompt, output_methods.success, True],
        [current_node.waitprompt, output_methods.success, False],
        [r'\[sudo\] password for', output_methods.new_send_pass(current_node.password), None],
        ["Sorry, try again.+password for", output_methods.get_pass, None],
    ]
    sudo_i_result = session.do(create_sequence('sudo -i', rows))
    if sudo_i_result:
        session.push_node(su_node)
        platform_run(session)
    return sudo_i_result

def sudo_i_add_sudoer(session):
    current_node = session.nodes[-1]
    su_node = base_node.SuNode(current_node, 'root')

    session.child.sendline('sudo -i')
    index = session.child.expect([
        su_node.waitprompt
        , current_node.waitprompt
        , r'\[sudo\] password for'
    ])
    if index == 0:
        session.push_node(su_node)
        platform_run(session)
        return True
    if index == 2:
        session.child.sendcontrol('c')
        session.child.expect(current_node.waitprompt)
        add_sudoer(session, current_node.username)

        if sudo_i_add_sudoer(session) is not True:
            print(ansi_colors.red("session aborted by command failure: sudo -i"))
            sys.exit(1)
        else:
            return True
    else:
        return False

def sudo_i(session):
    current_node = session.nodes[-1]
    if hasattr(current_node, 'platform'):
        if current_node.platform == 'ubuntu':
            return sudo_i_password(session)
    return sudo_i_add_sudoer(session)

def sudo_check(session):
    capt = run(session, 'timeout 1 sudo echo "" > /dev/null 2>&1; if [ $? -eq 0 ]; then echo "I" "am" "SUDOER";fi')
    for line in re.split('\r?\n', capt):
        if re.search('I am SUDOER', line):
            return True
    return False

def configure_sudo(session, username):
    sudoer_file = f'/etc/sudoers.d/{username}'
    run(session, f'echo "{username} ALL=(ALL) NOPASSWD: ALL" > {sudoer_file}')
    run(session, 'chmod 0440 ' + sudoer_file)

def ensure_user_sudoer(session):
    current_node = session.nodes[-1]
    if current_node.username != 'root':
        if not sudo_check(session):
            session.su()
            configure_sudo(session, current_node.username)
            session.su_exit()

def is_ping_ok(hostname_or_ip, count=2):
    def func(session):
        action = f'ping -c {count} {hostname_or_ip}'
        capture = run(session, action)
        base_msg = r'\d{1,2} packets transmitted, \d{1,2} received,'
        true_msg1 = base_msg + ' 0% packet loss, time '
        return bool(re.search(true_msg1, capture))
    return func

def here_doc(session, dst_file_path, contents, eof="'EOF'"):
    # 'EOF' avoids expanding variables
    curret = [['> ', output_methods.success, None]]
    session.do(create_sequence(f'cat << {eof} > {dst_file_path}', curret))
    _ = [session.do(create_sequence(content, curret)) for content in contents]
    run(session, eof.replace('"', '').replace("'", ''))


def heredoc_from_local(local_file_path, dst_file_path):
    def func(session):
        eof = "'EOF'"
        curret = [['> ', output_methods.success, None, '']]
        session.do(create_sequence(f'cat << {eof} > {dst_file_path}', curret))
        with open(local_file_path, 'r') as f:
            line = f.readline()
            while line:
                session.do(create_sequence(line.rstrip('\n'), curret))
                line = f.readline()
        run(session, eof.replace('"', '').replace("'", ''))
    return func

def remote_heredoc(local_file_path, dst_file_path):
    return heredoc_from_local(local_file_path, dst_file_path)

def work_on(session, work_dir, is_file_path=False):
    if is_file_path:
        work_dir = r"`dirname %s`" % work_dir
    return run(session, f'[ -d {work_dir} ] || mkdir -p {work_dir}; cd {work_dir}')

def create_dir(session, dir_path, is_file_path=False, sudo=False):
    if is_file_path:
        dir_path = r"`dirname %s`" % dir_path
    sudo_str = 'sudo' if sudo else ''
    action = f'[ -d {dir_path} ] || {sudo_str} mkdir -p {dir_path}'
    return run(session, action)

def create_backup(session, filename, backup_ext='.org', sudo=False):
    sudo_str = 'sudo' if sudo else ''
    action = f'[ -f {filename}{backup_ext} ] || {sudo_str} cp {filename} {filename}{backup_ext}'
    return run(session, action)

def check_test(session, test2):
    capt = run(session, f'{test2} && echo "Ye""sExists"')
    return bool('YesExists' in capt)

def check_line_exists_in_file(session, file_path, exp):
    return check_test(session, f"grep -q '{exp}' {file_path}")

def check_exists(session, name):
    return check_test(session, f'[ -e {name} ]')

def check_command_exists(session, command):
    return check_test(session, f'[ ! -z "`command -v {command}`" ]')

def check_file_exists(session, filename):
    return check_test(session, f'[ -f {filename} ]')

def check_dir_exists(session, dir_path, is_file_path=False):
    if is_file_path:
        dir_path = f'`dirname {dir_path}`'
    return check_test(session, f'[ -d {dir_path} ]')

def check_yes_or_no(session, eval_str):
    return check_test(session, f'[ {eval_str} ]')

def service_on(session, service):
    if base_node.is_platform_systemd(session.nodes[-1].platform):
        run(session, f'sudo systemctl enable --now {service}')
    else:
        run(session, f'sudo service {service} restart 2>&1')
        run(session, f'sudo chkconfig {service} on')

def service_off(session, service):
    if base_node.is_platform_systemd(session.nodes[-1].platform):
        run(session, f'sudo systemctl disable --now {service}')
    else:
        run(session, f'sudo service {service} stop')
        run(session, f'sudo chkconfig {service} off')

def patch(session, patchfile):
    action = f'patch < {patchfile}'
    reversepatch = r'Reversed \(or previously applied\) patch detected!  Assume -R\? \[n\]'
    applyanyway = r'Apply anyway\? \[n\]'
    rows = [[reversepatch, output_methods.send_line, 'n', 'Reversed patch detected.']]
    rows += [[applyanyway, output_methods.send_line, 'n', 'avoiding repatching']]
    rows += [['', output_methods.waitprompt, True, 'patched']]
    return session.do(create_sequence(action, rows))

def yum_rows():
    installcase = r'Is this ok \[y/N\]:'
    case1 = 'Complete!'
    case2 = 'Nothing to do'
    case3 = 'No packages in any requested group available to install or update'
    case4 = 'No [Pp]ackages marked for [Uu]pdate'
    return [
        [installcase, output_methods.send_line, 'y', "yum: Answering y"],
        [case1, output_methods.success, True, "yum: Complete!"],
        [case2, output_methods.success, False, "yum: Nothing to do"],
        [case3, output_methods.success, False, "yum: already installed"],
        [case4, output_methods.success, 'No Packages marked for Update', "yum: already updated"]
    ]

def yum_y(arg_list):
    return lambda session: run(session, f"sudo yum -y {' '.join(arg_list)}")

def yum_y_install(arg_list):
    return lambda session: yum_y(['install'] + arg_list)(session)

def yum_y_groupinstall(arg_list):
    return lambda session: yum_y(['groupinstall'] + arg_list)(session)

def yum_install(session, kwargs):
    rows = yum_rows()
    if 'update' in kwargs:
        if kwargs['update']:
            session.do(create_sequence('sudo yum -y update', rows))
            session.child.expect([session.waitprompt])

    if 'packages' in kwargs:
        packages = kwargs['packages']
        if isinstance(packages, list) and len(packages) > 0:
            action = f"sudo yum -y install {' '.join(packages)}"
            session.do(create_sequence(action, rows))
            session.child.expect([session.waitprompt])
    if 'group_packages' in kwargs:
        group_packages = kwargs['group_packages']
        if isinstance(group_packages, list) and len(group_packages) > 0:
            pkg_str = '", "'.join(group_packages)
            action = f'sudo yum -y groupinstall "{pkg_str}"'
            session.do(create_sequence(action, rows))
            session.child.expect([session.waitprompt])

def count_by_egrep(session, expression, filename):
    test = f"if [ `egrep -c '{expression}' {filename}` -gt 0 ]; "
    return check_test(session, test)

def if_exists_by_grep_str(exp, file_path):
    return f'grep -q {exp} {file_path} && '

def if_not_exists_by_grep_str(exp, file_path):
    return f'grep -q {exp} {file_path} || '

def sed_e_separator(src_exp, dst_exp):
    for sep in [
        '/'
        , '*'
        , '%'
        , ':'
        , '@'
        , '#'
    ]:
        if sep in src_exp or sep in dst_exp:
            pass
        else:
            return sep
    return False

def create_sed_e_replace_str(src_exp, dst_exp):
    """
    >>> create_sed_e_replace_str('^#test$', 'test')
    "'s/^#test$/test/'"
    >>> create_sed_e_replace_str('^#/var/*$', '/var/*')
    "'s%^#/var/*$%/var/*%'"
    """
    sep = sed_e_separator(src_exp, dst_exp)
    if "'" in src_exp:
        if '"' in src_exp:
            print(ansi_colors.red('sed replace can not handle single and double quote simultaneously in src_exp'))
            exit(1)
        else:
            return f'"s{sep}{src_exp}{sep}{dst_exp}{sep}"'
    else:
        return f"'s{sep}{src_exp}{sep}{dst_exp}{sep}'"

def sed_replace_str(src_exp, dst_str, src_file, dst_file=None):
    sed_e_replace_str = create_sed_e_replace_str(src_exp, dst_str)
    if dst_file is None or src_file == dst_file:
        action = f"sed --in-place -e {sed_e_replace_str} {src_file}"
    else:
        action = f"sed -e {sed_e_replace_str} {src_file} > {dst_file}"
    return action

def sed_replace(session, src_exp, dst_str, src_file, dst_file=None):
    return run(session, sed_replace_str(src_exp, dst_str, src_file, dst_file))

def sed_replace_if_exists(session, src_exp, dst_str, src_file, dst_file=None):
    if_exists_str = if_exists_by_grep_str(src_exp, src_file)
    return run(session, if_exists_str + sed_replace_str(src_exp, dst_str, src_file, dst_file))

def sed_pipe_str(src_file, dst_file, exp_list):
    action = ''
    for i, exp in enumerate(exp_list):
        s_exp = exp[0]
        d_exp = exp[1]
        sed_e_replace_str = create_sed_e_replace_str(s_exp, d_exp)
        if i == 0:
            action = f"sed -e {sed_e_replace_str} {src_file}"
        else:
            action += f" | sed -e {sed_e_replace_str}"
    action += f' > {dst_file}'
    return action

def sed_pipe(session, src_file, dst_file, exp_list):
    return run(session, sed_pipe_str(src_file, dst_file, exp_list))

def sed_delete_between_pattern_str(file_path, start_exp='^####PLUR_START', end_exp='^####PLUR_END'):
    sep = sed_e_separator(start_exp, end_exp)
    return f"sed -ie '{sep}{start_exp}{sep},{sep}{end_exp}{sep}d' {file_path}"

def delete_between_pattern(file_path, start_exp='^####PLUR_START', end_exp='^####PLUR_END'):
    return lambda session: run(session, sed_delete_between_pattern_str(file_path, start_exp, end_exp))

def sed_append_after_pattern_str(file_path, exp, line):
    sep = sed_e_separator(exp, exp)
    if line == '':
        command = 'G'
    else:
        command = f'a {line}'
    return f"sed -ie '{sep}{exp}{sep}{command}' {file_path}"

def grep_exist_pattern_str(file_path, exp):
    return f"grep -qe '{exp}' {file_path}"

def append_line_after_match(file_path, exp, line):
    return lambda session: run(session, sed_append_after_pattern_str(file_path, exp, line))

def append_line_after_match_if_not_exists(file_path, exp, line):
    return lambda session: run(session, f"{grep_exist_pattern_str(file_path, exp)} || {sed_append_after_pattern_str(file_path, exp, line)}")

def append_line(line, file_path):
    def func(session):
        re_line = re.sub(r'\$', r'\\$', line)
        if not count_by_egrep(session, re_line, file_path):
            run(session, f"echo '{line}' >> {file_path}")
    return func

def append_bashrc(session, line):
    bashrc = '$HOME/.bashrc'
    re_line = re.sub(r'\$', r'\\$', line)
    if not count_by_egrep(session, re_line, bashrc):
        run(session, f"echo '{line}' >> {bashrc}")
    run(session, 'source ' + bashrc)

def append_lines(session, file_path, lines):
    create_backup(session, file_path)
    for line in lines:
        run(session, f'echo {line} >> {file_path}')

def idempotent_append(session, file_path, expression, line):
    action = f"grep -q '{expression}' {file_path} || echo '{line}' >> {file_path}"
    return run(session, action)

def wget(session, url=None, option=None):
    if url is None:
        url = 'http://sample.local'
    if option is None:
        option = ''
    action = f'wget {option} {url}'
    success_case = r' saved \['
    fail_case1 = 'ERROR 404: Not Found.'
    fail_case2 = 'wget: unable to resolve host address'
    fail_case3 = 'failed: No route to host.'
    rows = [
        [success_case, output_methods.success, True, ''],
        [fail_case1, output_methods.success, False, ''],
        [fail_case2, output_methods.success, False, ''],
        [fail_case3, output_methods.success, False, '']
    ]
    result = session.do(create_sequence(action, rows))
    session.child.expect(session.waitprompt)
    return result
