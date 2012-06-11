
# Error for when using a user-specified option with a VBoxManage command fails
class UnknownOptionError(Exception):
    def __init__(self, cmd, option):
        self.cmd = cmd
        self.option = option

    def __str__(self):
        return "Unknown Option " + self.option + " for command " + self.cmd


# Error for when the VM specified by name and UUID is unrecognized
class UnknownVMError(Exception):
    def __init__(self, name, uuid):
        self.name = str(name)
        self.uuid = str(uuid)

    def __str__(self):
        return "No VM found for name " + self.name + " and UUID " + self.uuid
