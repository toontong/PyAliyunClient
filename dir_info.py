#coding:utf8
#TooNTonG 2012-08-21

import os
import logging
import fileutils

from database import SafeSerialize

class BucketPathInfo(SafeSerialize):
    '''远程的bucket信息'''

class DirectoryInfo(SafeSerialize, dict):
    '''本地文件结构信息
    key  为 文件绝对路径，unicode
    value为 FileInfo or PathInfo
    '''

class FileInfo(object):
    def __init__(self, fname, md5 = ''):
        assert isinstance(fname, unicode)
        '''fname : 文件绝对路径, unicode'''
        self.fname = fname
        self.md5 = md5.lower()
        self.mtime = fileutils.mtime(fname)
        self.size = fileutils.size(fname)
        self.isFile = True

    def is_changed(self):
        return (self.mtime != fileutils.mtime(self.fname) and self.mtime >= 0) or \
            self.size != fileutils.size(self.fname)

class PathInfo(object):
    def __init__(self, fname):
        assert isinstance(fname, unicode)
        '''fname : 文件绝对路径,unicode'''
        self.isFile = False
        self.fname = fname


