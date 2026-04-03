import shlex
ALLOWED = ['echo', 'ls', 'dir']
def is_allowed(cmd): return shlex.split(cmd)[0] in ALLOWED if cmd else False
