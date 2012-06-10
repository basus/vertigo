import subprocess
import constants

from error import *

def version():
    return subprocess.check_output([constants.cmd, "-v"])

def list(option="all", longform=False):

    cmd = [constants.cmd, "list"]

    if longform:
        cmd.append("--long")

    if not option in constants.lsopts and not option == "all":
        raise UnknownOptionError("list", option)

    if option == "all":
        result = {}
        for opt in constants.lsopts:
            result[opt] = subprocess.check_output(cmd + [opt])
        return result
    else:
        return subprocess.check_output(cmd + [option])


def createvm(name,ostype=None,register=False,basefolder=None,uuid=None):
    cmd = [constants.cmd, "createvm", "--name", name]

    if ostype:
        cmd += ["--ostype", ostype]
    if register:
        cmd += ["--register"]
    if basefolder:
        cmd += ["--basefolder", basefolder]
    if uuid:
        cmd += ["--uuid", uuid]

    # TODO: change to return VM object
    return subprocess.check_output(cmd)

class VM(object):

    def __init__(self, name=None, uuid=None):
        if name == None and uuid == None:
            raise UnknownVMError(name, uuid)

        if not name:
            argid = uuid
        else:
            argid = name

        try:
            args = [constants.cmd, "showvminfo", "--machinereadable", argid]
            self.vminfo = subprocess.check_output(args)
        except CalledProcessError:
            raise UnknownVMError(name, uuid)

        self.info = self.parse_info(self.vminfo)
        self.name = self.info['name']
        self.uuid = self.info['UUID']


    def parse_info(self, rawinfo=None,machine=True):
        if not rawinfo:
            rawinfo = self.vminfo

        info = {}
        longkey = None
        longval = None

        if machine:
            sep = "="
        else:
            sep = ":"

        for line in rawinfo.splitlines():
            parts = line.split(sep)

            # Work with multiline key-value pairs
            if not machine:
                if len(parts) == 1 and not longkey:
                    longkey = parts[0].strip()
                    longval = ""
                    continue
                elif len(parts) == 1:
                    longval + "\n"
                    longval += line
                    continue
                else:
                    longkey = None
                    longval = None

                key = parts[0].strip()
                value = ':'.join(parts[1:]).strip()
            else:
                key = parts[0].strip()
                value = parts[1].strip(' \"')

            # Turn numbers to ints
            try:
                value = int(value)
            except ValueError:
                pass

            # Turn on/off/none to True/False/None
            if value == "on":
                value = True
            elif value == "off":
                value = False
            elif value == "none":
                value = None

            info[key] = value

        return info


    def showvminfo(self, details=False, machine=True):
        args = [constants.cmd, "showvminfo"]

        if details:
            args += ["--details"]
        if machine:
            args += ["--machinereadable"]

        args += [self.uuid]

        info = subprocess.check_output(args)
        parsed =  self.parse_info(info, machine)
        parsed['string'] = info
        return parsed

