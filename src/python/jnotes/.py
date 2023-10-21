import re
import os
if not 'id_0123456789876543210' in locals():
    _rootlevel = 3
    _oldwd = re.sub(r'\\', '/', os.getcwd())
    _spdirs = _oldwd.split('/')
    _newwd = '/'.join(_spdirs[:(len(_spdirs)-_rootlevel)])
    os.chdir(_newwd)
    id_0123456789876543210 = None
print(f'Old WD: {_oldwd}')
print(f'New WD: {_newwd}')
