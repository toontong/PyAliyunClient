#coding:utf8
#TooNTonG 2012-08-13
import os
import hashlib
import traceback

def mtime(filename):
    try:return os.path.getmtime(filename)
    except:
        traceback.print_exc()
        return 0

def size(fname):
    try:os.path.getsize(fname)
    except:
        traceback.print_exc()
        return 0

def md5(fname):
    try:
        s = 8192
        m = hashlib.md5()
        fp = open(fname, 'rb')
        d = fp.read(s)
        while d:
            m.update(d)
            d = fp.read(s)
        return m.hexdigest()
    except:
        traceback.print_exc()
        return ''
