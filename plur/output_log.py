import sys
from mini import misc

class CreateInstance:
    def __init__(self, log_params):
        self.file_writer_list = []
        self.file_path = None
        if 'output_log_file_path' in log_params:
            self.file_path = log_params['output_log_file_path']
            self.file_writer_list.append(misc.ForkWriter(self.file_path, 'w'))

        self.append_file_path = None
        if 'output_log_append_path' in log_params:
            self.append_file_path = log_params['output_log_append_path']
            self.file_writer_list.append(misc.ForkWriter(self.append_file_path, 'a'))

        if 'enable_stdout' in log_params and log_params['enable_stdout']:
            self.enable_stdout = True
            self.stdout = sys.stdout
        else:
            self.enable_stdout = None
            self.stdout = misc.FakeWriter()

    def pause_output(self):
        if self.enable_stdout:
            self.stdout = misc.FakeWriter()
        self.close()

    def continue_output(self):
        if self.enable_stdout:
            self.stdout = sys.stdout

        if self.file_path:
            self.file_writer_list.append(misc.ForkWriter(self.file_path, 'a'))
        if self.append_file_path:
            self.file_writer_list.append(misc.ForkWriter(self.append_file_path, 'a'))
        return self

    def add_file_writer(self, additional_file_path=None, write_mode='w'):
        if additional_file_path:
            self.file_writer_list.append(misc.ForkWriter(additional_file_path, write_mode))

    def write(self, message):
        self.stdout.write(message)
        for file_writer in self.file_writer_list:
            file_writer.write(message)

    def flush(self):
        self.stdout.flush()
        for file_writer in self.file_writer_list:
            file_writer.flush()

    def close(self):
        self.stdout.flush()
        for file_writer in self.file_writer_list:
            file_writer.flush()
            file_writer.close()
        self.file_writer_list = []
