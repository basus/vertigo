
class UnknownOptionError(Exception):
    def __init__(self, cmd, option):
        self.cmd = cmd
        self.option = option

    def __str__(self):
        return "Unknown Option " + self.option + " for command " + self.cmd

