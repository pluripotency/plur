import os
import time
import shutil
from plur import debug_log
from plur import output_log
from plur import log_param_templates

def run_delete_mtime(log_params):
    if log_params and 'log_dir' in log_params and 'delete_mtime' in log_params and 'delete_mtime_unit' in log_params:
        log_dir = log_params['log_dir']
        delete_mtime = log_params['delete_mtime']
        delete_mtime_unit = log_params['delete_mtime_unit']
        if os.path.isdir(log_params['log_dir']) and isinstance(delete_mtime, int) and delete_mtime_unit in ['sec', 'min', 'hour', 'day']:
            now = time.time()
            if delete_mtime_unit == 'day':
                mtime_before = now - delete_mtime * 60 * 60 * 24
            elif delete_mtime_unit == 'min':
                mtime_before = now - delete_mtime * 60
            elif delete_mtime_unit == 'hour':
                mtime_before = now - delete_mtime * 60 * 60
            else:
                # sec
                mtime_before = now - delete_mtime
            for curdir, dirs, files in os.walk(log_dir):
                for d in dirs:
                    target = os.path.join(curdir, d)
                    if os.path.getmtime(target) < mtime_before:
                        shutil.rmtree(target, ignore_errors=True)
                for f in files:
                    target = os.path.join(curdir, f)
                    if os.path.getmtime(target) < mtime_before:
                        shutil.rmtree(target, ignore_errors=True)

class Initialize:
    def __init__(self, log_params=None):
        run_delete_mtime(log_params)
        if log_params is None:
            env_log_params = log_param_templates.select(os.environ.get('LOG_PARAMS'))
            if env_log_params:
                log_params = env_log_params
            else:
                log_params = log_param_templates.only_stdout()

        self.output_log = output_log.CreateInstance(log_params)
        self.debug_log = debug_log.CreateInstance(log_params)

    def message(self, message):
        self.debug_log.message(message)

    def close(self):
        if hasattr(self, 'output_log'):
            self.output_log.close()
        if hasattr(self, 'debug_log'):
            self.debug_log.close()

