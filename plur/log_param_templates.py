from mini import misc

def normal_on_tmp():
    now = misc.now()
    ymd = misc.get_ymd(now)
    hms_f = misc.get_hms_f(now)
    log_dir = '/tmp/plur_log'
    log_params = {
        'log_dir': log_dir,
        'enable_stdout': True,
        'output_log_file_path': f'{log_dir}/{ymd}/output_{hms_f}.log',
        'dont_truncate': False,
        'debug_color': True,
        'debug_log_file_path': f'{log_dir}/{ymd}/debug_{hms_f}.log',
        'delete_mtime_unit': 'day',
        'delete_mtime': 10,
    }
    return log_params

def normal():
    return normal_on_tmp()

def append():
    log_params = normal()
    log_dir = log_params['log_dir']
    log_params['output_log_append_path'] = f'{log_dir}/output_append.log'
    log_params['debug_log_append_path'] = f'{log_dir}/debug_append.log'
    return log_params

def debug():
    log_params = append()
    log_params['dont_truncate'] = True
    return log_params

def append_on_tmp():
    log_params = normal_on_tmp()
    log_dir = log_params['log_dir']
    log_params['output_log_append_path'] = f'{log_dir}/output_append.log'
    log_params['debug_log_append_path'] = f'{log_dir}/debug_append.log'
    return log_params

def debug_on_tmp():
    log_params = append_on_tmp()
    log_params['dont_truncate'] = True
    return log_params

def only_stdout():
    log_params = {
        'enable_stdout': True
    }
    return log_params

def silent():
    return {}

def with_hostname(hostname):
    log_params = normal()
    log_dir = log_params['log_dir']
    log_params['output_log_file_path'] = f'{log_dir}/output_{hostname}.log'
    log_params['debug_log_file_path'] = f'{log_dir}/debug_{hostname}.log'
    return log_params

def select(env_str):
    if env_str == 'only_stdout':
        return only_stdout()
    if env_str == 'normal_on_tmp':
        return normal_on_tmp()
    if env_str == 'append_on_tmp':
        return append_on_tmp()
    if env_str == 'debug_on_tmp':
        return debug_on_tmp()
    if env_str == 'normal':
        return normal()
    if env_str == 'append':
        return append()
    if env_str == 'debug':
        return debug()
    return normal()
