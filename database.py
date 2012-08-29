#coding:utf-8
#
# author: chuantong.huang@gmail.com
#

import os
import zlib
import cPickle as pickle
import traceback
import logging
from threading import RLock

class _FileProtector:
    def __init__(self):
        self._locks = {}

    def acquire(self, _file):
        if not self._locks.has_key(_file):
            self._locks[_file] = RLock()
        self._locks[_file].acquire()

    def release(self, _file):
        assert self._locks.has_key(_file), _file
        try:
            self._locks[_file].release()
        except Exception, e:
            print 'FileProtector', e, _file
            for k, r in self._locks.items():
                print k, 'r._RLock__count', r._RLock__count, r._is_owned(), r
            #raise e

class SerializeBase:
    _protector = _FileProtector()

    @staticmethod
    def load(filepath, constructor):
        if not os.path.exists(filepath):
            obj = constructor()
            obj._file = filepath
            return obj

        fp = None
        SerializeBase._protector.acquire(filepath)
        try:
            fp = open(filepath, 'rb')
            obj = pickle.loads(zlib.decompress(fp.read()))
            obj._file = filepath
            obj._loadFromFile = True
        except:
            logging.error('Error on load [%s] ...' % filepath)
            logging.error(traceback.format_exc())

            obj = constructor()
            obj._file = filepath
        finally:
            try:
                if fp: fp.close()
            except:
                logging.error(traceback.format_exc())
            finally:
                SerializeBase._protector.release(filepath)
        return obj

    def isLoadSuccess(self):
        return hasattr(self, '_loadFromFile') and self._loadFromFile

    def save(self):
        if not hasattr(self, '_file'):
            return

        _f = self._file

        pfolder = os.path.split(os.path.realpath(_f))[0]
        if pfolder and not os.path.exists(pfolder):
            os.makedirs(pfolder)

        SerializeBase._protector.acquire(_f)
        fp = None
        try:
            fp = open(_f, 'wb')
            fp.write(zlib.compress(pickle.dumps(self, True)))
            fp.flush()
            os.fsync(fp)
            fp.close()
            fp = None
            return True
        except:
            logging.error('Error on serialize [%s] ...' % _f)
            logging.error(traceback.format_exc())
        finally:
            try:
                if fp: fp.close()
            except:
                logging.error(traceback.format_exc())
            finally:
                SerializeBase._protector.release(_f)

def _safeMtime(filename):
    try:return os.path.getmtime(filename)
    except:return 0

class SafeSerialize(SerializeBase):

    @staticmethod
    def load(filepath, constructor):
        f1, f2 = u'%s.A' % filepath, u'%s.B' % filepath

        def loadFunc(fname):
            obj = SerializeBase.load(fname, constructor)
            return obj.isLoadSuccess(), obj

        # NOTE：先加载修改时间较新的文件A，如何加载失败，改加载文件B
        A, B = (f1, f2) if _safeMtime(f1) >= _safeMtime(f2) else (f2, f1)

        ret, obj = loadFunc(A)
        if ret is False:
            #logging.warning('load db A[%s] was failed, will try load B[%s].' % (A, B))
            ret, obj = loadFunc(B)

#        if ret is False:
#            logging.warning('load two db file ware failed.')

        return obj

    def save(self):
        # NOTE：保存文件时采用轮流写A、B文件的方式
        if not hasattr(self, '_file'):
            return
        _file = self._file
        if _file.endswith('.A'):
            self._file = u'%s.B' % _file[:-2]
        elif _file.endswith('.B'):
            self._file = u'%s.A' % _file[:-2]
        elif _file.endswith('.db'):
            self._file = u'%s.A' % _file
        return SerializeBase.save(self)

    def remove(self):
        if not hasattr(self, '_file'):
            return
        _file = self._file
        if os.path.exists("%s.A" % _file[:-2]):
            os.remove("%s.A" % _file[:-2])
        if os.path.exists("%s.B" % _file[:-2]):
            os.remove("%s.B" % _file[:-2])

if __name__ == '__main__':
    v1 = {1:1234}
    v2 = {1:654321}
    class Test(SafeSerialize):
        def __init__(self):
            self.var = v1
    file = 'c:\\tmp_test_elive_serialize_lkjslkjdf22323'
    assert not os.path.exists(file)
    t = Test.load(file, Test)
    assert t.var == v1, t.var
    t.var = v2
    t.save()
    t = Test.load(file, Test)
    assert t.var == v2, (t.var, v2)
    t.remove()
    print 'end'
