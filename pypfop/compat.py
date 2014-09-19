import sys

if sys.version_info.major < 3:
    BASE_STRING = basestring
else:
    BASE_STRING = str

def debug_msg(log, msg, label=''):
    if isinstance(msg, BASE_STRING):
        log.debug('{}: {}'.format(label, msg))
    else:
        log.debug('{}: {}'.format(label, msg.decode())) # bytes
