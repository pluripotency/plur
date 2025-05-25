import os
from mini import misc
from mini import ansi_colors

class CreateInstance:
    def __init__(self, log_params):
        self.file_path = None
        if 'debug_log_file_path' in log_params:
            self.file_path = os.path.expanduser(log_params['debug_log_file_path'])
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        self.append_path = None
        if 'debug_log_append_path' in log_params:
            self.append_path = os.path.expanduser(log_params['debug_log_append_path'])
            os.makedirs(os.path.dirname(self.append_path), exist_ok=True)
        self.f = misc.ForkWriter(self.file_path)
        self.af = misc.ForkWriter(self.append_path)

        self.dont_truncate = False
        if 'dont_truncate' in log_params:
            self.dont_truncate = log_params['dont_truncate']

        self.debug_color = True
        if 'debug_color' in log_params:
            self.debug_color = log_params['debug_color']
        ansi_colors.set_colors(self, self.debug_color)

    def on_action(self, session, action):
        if self.file_path or self.append_path:
            self.write_line(misc.now_debug() + ' action sent: ' + self.yellow(action))
            if hasattr(session, 'nodes'):
                current_node = session.nodes[-1]
                for attr in ['hostname', 'access_ip', 'username', 'waitprompt', 'platform']:
                    if hasattr(current_node, attr):
                        self.write_line(self.light_cyan(('         '+attr)[-14:] + ': ' + str(getattr(current_node, attr))))
            self.write_line(self.light_cyan(('         ' + 'timeout')[-14:] + ': ' + str(session.timeout)))
            self.flush()

    def at_row_method(self, message):
        if self.file_path or self.append_path:
            self.write_line(misc.now_debug() + f' {self.brown(message)}')

    def before_select(self, session, output_list):
        if self.file_path or self.append_path:
            self.write_line(misc.now_debug() + ' selection:')
            for i, output in enumerate(output_list):
                self.write_line(self.pink(f"{i}       expect: %s" % repr(output[0])))
                self.write_line(self.purple("      reaction: %s" % output[1]))
                if len(output) > 2:
                    self.write_line(self.purple("          args: %s" % output[2]))
            self.flush()

    def after_select(self, session, selected_index):
        if self.file_path or self.append_path:
            self.write_line(misc.now_debug() + self.pink(f' selected: {selected_index}'))
            if hasattr(session, 'child'):
                if hasattr(session.child, 'before'):
                    if self.dont_truncate:
                        self.write_line(self.brown('        before: ' + repr(session.child.before)))
                    else:
                        before = session.child.before
                        if len(before) > 160:
                            self.write_line(self.brown('        before: truncated: ' + repr(before[-160:])))
                        else:
                            self.write_line(self.brown('        before: ' + repr(before)))

                    self.write_line(self.red('       matched: ' + repr(session.child.after)))
                    self.write_line(self.cyan('        buffer: ' + repr(session.child.buffer)))
            self.flush()

    def message(self, message):
        if self.file_path or self.append_path:
            if isinstance(message, str):
                mes = message
            else:
                mes = str(message)
            self.write(misc.now_debug() + ' ' + mes)
            self.flush()

    def exit1_with_message(self, message):
        self.message(message)
        exit(1)

    def write_line(self, message):
        self.f.write(message + '\n')
        self.af.write(message + '\n')

    def write(self, message):
        self.f.write(message)
        self.af.write(message)

    def flush(self):
        self.f.flush()
        self.af.flush()

    def close(self):
        self.f.flush()
        self.af.flush()
        self.f.close()
        self.af.close()


