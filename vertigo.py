import subprocess
import constants

from error import *

# functions that don't fall into the VM class

# Return the current Virtualbox version as a string
def version():
    return subprocess.check_output([constants.cmd, "-v"])

# Public: List available virtual machines, virtual devices and their relevant
# properties. Currently only returns a string representation. Will eventually
# return a more structured format, probably a dictionary
#
# option - the resource to list. Possible options listed in constants.py and the
#          VBoxManage manual
# longform - supply the --long switch to VBoxManage. Only relevant for a few
# options
#
# Returns a string representation of the requested option, or a dictionary of
# all of them
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

# Public: Create a new virtual with the given options.
#
# name - String that is the name of the new VM
# ostype - String that should be the OS type
# register - Boolean whether or not to register this VM in Virtualbox
# basefolder - String giving the path where to store the VM files
# uuid - Hexadecimal String to be the UUID of the VM
#
# Returns a VM object (eventually) wrapping the VM 
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

# Public: Register a VM from its XML file
#
# filename - String giving the filepath to the XML file to use
#
# Returns True if the registration succeeded.
# Raises RegistrationError otherwise
def registervm(self, filename):
    args = [constants.cmd, "registervm", filename]

    try:
        result = subprocess.check_output(args)
    except CalledProcessError as e:
        raise RegistrationError(filename, e)

    return True

# Public: Class that wraps a Virtualbox VM and lets you interact with it and
# configure. Does not interact with the Guest OS in any way.
class VM(object):

    # Public: Initialize a VM object to wrap a particular Virtualbox VM. At
    # least one of name or UUID must be provided to locate the VM and the VM
    # referenced must already exist.
    #
    # name - String that is the name of VirtualBox VM.
    # uuid - Hexadecimal String that is the UUID of the VirtualBox VM.
    #
    # Returns a VM object wrapping the VirtualBox VM
    # Raises UnknownVMError if VM corresponding to the name or UUID is not found
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


    # Public: Parse a raw VM information string as returned by showvminfo and
    # turn it into a machine-usable Python dictionary.
    #
    # rawinfo - String that is the raw information dump from showvminfo
    # machine - Boolean saying if the raw information is from using the
    #           machinereadable switch
    # pythonize - Boolean saying if values should be swapped with their Python
    #             equivalents (True for on, False for off, None for <none>)
    #
    # Returns a dictionary of information keys to their provided values
    def parse_info(self, rawinfo=None,machine=True, pythonize=True):
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

            if pythonize:
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


    # Public: Create a Python dictionary representing the output from the
    # showvminfo command. Uses parse_info to parse the raw string and places the
    # raw string into a 'string' key in the dictionary.
    #
    # details - Boolean to use the --details flag
    # machine - Boolean to use the --machinereadable flag (easier to parse)
    # pythonize - Boolean saying if values should be swapped with their Python
    #             equivalents (True for on, False for off, None for <none>)
    #
    # Returns the parsed dictionary representation
    def showvminfo(self, details=False, machine=True, pythonize=True):
        args = [constants.cmd, "showvminfo"]

        if details:
            args += ["--details"]
        if machine:
            args += ["--machinereadable"]

        args += [self.uuid]

        info = subprocess.check_output(args)
        parsed =  self.parse_info(info, machine, pythonize)
        parsed['string'] = info
        return parsed


    # Public: Unregister the VM and optionally delete
    #
    # delete - Boolean to delete the VM as well as unregister
    #
    # Returns True if unregistering was successful
    # Raises the generic CommandError otherwise
    def unregistervm(self, delete=False):
        args = [constants.cmd, "unregistervm", self.uuid]
        if delete:
            args += ["--delete"]
        try:
            result = subprocess.check_output(args)
        except CalledProcessError as e:
            raise CommandError(args, e)

        return True
