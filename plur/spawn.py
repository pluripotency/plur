from plur.output_methods import handle_output, pexpect, child_send, child_sendcontrol, child_sendline
from plur import logger


class Spawn:
    def __init__(self, log_params=None):
        """
        child is pexpect child
        """
        self.child = None
        self.default_timeout = 600
        self.timeout = 600

        # logger is enabled in Session
        self.logger = logger.Initialize(log_params)

    def validate_timeout(self, timeout):
        if isinstance(timeout, int):
            if 0 < timeout <= 86400:
                return timeout
            self.logger.debug_log.message(f"WARN: invalid timeout: out of range: {timeout}")
            return self.default_timeout
        self.logger.debug_log.message(f"WARN: invalid timeout: not integer: {timeout}")
        return self.default_timeout

    def set_timeout(self, timeout=None):
        self.timeout = self.validate_timeout(timeout)
        if self.child:
            self.child.timeout = self.timeout

    def set_default_timeout(self, timeout):
        self.default_timeout = self.validate_timeout(timeout)

    def do(self, seq, timeout=None):
        action = seq[0]
        outputs = seq[1]
        method_type = seq[2]
        self.action_handler(action, method_type)
        if timeout:
            self.set_timeout(timeout)
        result = handle_output(self, outputs)
        if timeout:
            self.set_timeout()
        return result

    def action_handler(self, action, method_type):
        """
        about codec_errors
        https://github.com/pexpect/pexpect/issues/401
        """
        if self.child is None:
            # Starting pexpect
            # If pexpect instance is None, spawn and start command log
            self.logger.debug_log.message(f'Spawning by: {action}')
            self.child = pexpect.spawn(
                action
                , timeout=self.timeout
                , logfile=self.logger.output_log
                , echo=True
                , encoding='utf8'
                , codec_errors='replace'
            )
        else:
            if method_type is None:
                self.child.sendline(action)
            elif isinstance(method_type, str):
                if hasattr(self.child, method_type) and method_type in [
                    child_sendcontrol,
                    child_send,
                    child_sendline
                ]:
                    getattr(self.child, method_type)(action)
                else:
                    self.logger.debug_log.exit1_with_message(f'error in action_handler: no such method_type: {method_type}')
            else:
                self.logger.debug_log.exit1_with_message('error in action_handler: method_type must be str')
        self.logger.debug_log.on_action(self, action)

    def close(self):
        self.logger.debug_log.message("INFO:Closing session.")
        self.logger.close()
        self.child.close()
