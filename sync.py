#coding:utf8
#TooNTonG 2012-08-13

import os
import locale
import logging
import fileutils
from dir_info import DirectoryInfo, PathInfo, FileInfo
import posixpath
path_join = posixpath.join


class BucketWorker(object):
    def __init__(self, aliyun, sync_path, bucket, c = False):
        self._api = aliyun
        self._path = sync_path if isinstance(sync_path, unicode) else sync_path.decode('utf8')
        self._bucket = bucket
        self._abort = False

    def load_directory_info(self, prefix):
        if prefix.endswith(r'/'):
            prefix = prefix[:-1]

        path = path_join(self._path, self._bucket.name.decode('utf8'), prefix.decode('utf8'))
        sync_path = path_join(path, u'.sync')
        if not os.path.exists(sync_path):
            os.mkdir(sync_path)
        os.chmod(sync_path, 16895)
        filepath = path_join(sync_path, '.dirinfo.db')
        return DirectoryInfo.load(filepath, DirectoryInfo)

    def abort(self):
        self._abort = True

    def run(self):
        raise NotImplementedError()

class DownBucketWorker(BucketWorker):

    def _new_folder(self, name, dirinfo):
        path = path_join(self._path, name.decode('utf8'))
        if os.path.exists(path):
            if os.path.isfile(path):
                raise TypeError('[%s] was a exists file' % path)
        else:
            os.mkdir(path)
        if not dirinfo.has_key(path):
            dirinfo[path] = PathInfo(path)

    def _new_file(self, key_name, etag, dirinfo):
        '''
        etag是md5值
        '''
        # 如果是文件夹，返回
        if key_name.endswith(r'/'):
            return

        unicode_key_name = key_name.decode('utf8')

        savename = path_join(self._path,
              self._bucket.name.decode('utf8'),
              unicode_key_name)

        etag = etag.replace('"', '').lower()

        if os.path.exists(savename):
            fileinfo = dirinfo.get(savename)
            if fileinfo and not fileinfo.is_changed() and fileinfo.md5 == etag:
                logging.info('file not changed')
                return
            elif fileinfo and fileinfo.is_changed():
                if fileinfo.md5 != etag and fileutils.md5(savename) != etag:
                    logging.error('file [%s] conflict.' % unicode_key_name)
                    print "TODO：旧文件存在，并发了改变,生成冲突，请用户选择：覆盖还是跳过 1"
                elif fileinfo.md5 == etag:
                    logging.info('the same file md5, just mtime changed.')
                    dirinfo[savename] = FileInfo(savename, etag)
                    dirinfo.save()
                    return
            elif not fileinfo:
                if fileutils.md5(savename) == etag:
                    logging.info('the same file md5.')
                    dirinfo[savename] = FileInfo(savename, etag)
                    dirinfo.save()
                    return
                else:
                    logging.warning('file [%s] conflict.' % unicode_key_name)
                    print "TODO：文件存在，第一次同步的，生成冲突，请用户选择：覆盖还是跳过 2"
                    return

        return self.__download(unicode_key_name, etag, savename, dirinfo)

    def __download(self, unicode_key_name, etag, savename, dirinfo):
        tmpfile = savename + u'.tmp'

        def callback(file_object):
            if not os.path.exists(tmpfile):
                logging.warning(u'down object[%s] failed.' % unicode_key_name)
                return

            try:
                os.rename(tmpfile, savename)
            except Exception, e:
                logging.error('_new_file.callback.rename [%s]' % e)
            if not dirinfo.has_key(savename):
                dirinfo[savename] = FileInfo(savename, etag)
                dirinfo.save()

        self._api.get_object_to_file(callback,
                                     self._bucket.name,
                                     unicode_key_name,
                                     tmpfile)

    def _make_prefix(self, prefix, marker = '', max_key = ''):
        '''广度递归，对文件夹一层层 同步下载文件'''
        delimiter = '/'
        dirinfo = self.load_directory_info(prefix)

        def callback(root_bucket):
            for p in root_bucket.prefix_list:
                self._new_folder(path_join(self._bucket.name, p[:-1]), dirinfo)
            dirinfo.save()
            for c in root_bucket.content_list:
                self._new_file(c.key, c.etag, dirinfo)

            for p in root_bucket.prefix_list:
                self._make_prefix(prefix = p)

        self._api.get_bucket(
            callback,
            self._bucket.name,
            prefix, marker,
            delimiter, max_key)

    def run(self):
        # 1st. create bucket folder
        self._new_folder(self._bucket.name, {})
        self._make_prefix('')
        print 'end run'

def is_filter_file(name):
    startswith = ['.', '~']
    endswith = ['.%%%', '.@@@', '.$$$', '.___', '._mp', '.~mp', '.tmp', ]
    for str in startswith:
        if name.startswith(str):
            return True
    for str in endswith:
        if name.endswith(str):
            return True
    return False

#ENCODE = locale.getpreferredencoding()

class UpBucketWorker(BucketWorker):
    def __init__(self, aliyun, sync_path, bucket, c = False):
        BucketWorker.__init__(self, aliyun, sync_path, bucket, c)
        self._abspath_len = len(path_join(self._path, self._bucket.name.decode('utf8')))

    def _split_prefix(self, abspath):
        assert len(abspath) >= self._abspath_len + 1
        return abspath[self._abspath_len + 1:]

    def _abspath(self, prefix):
        return path_join(self._path, self._bucket.name.decode('utf8'), prefix)

    def run(self):
        p = path_join(self._path, self._bucket.name.decode('utf8'))
        prefix = u''
        self._up_path_to_bucket(prefix , p)

    def _up_path_to_bucket(self, prefix, parent_path):
        if not os.path.exists(parent_path):
            logging.info('path not exists')
            return

        bucket_name = self._bucket.name
        dirinfo = self.load_directory_info(prefix)

        folders = []

        set_local = set()
        set_has_synced = set(dirinfo.keys()) # 本地已同步好的文件会在此集合中

        # fname is unicode
        for fname in os.listdir(parent_path):
            if is_filter_file(fname):
                continue
            abspath = path_join(parent_path, fname)
            set_local.add(abspath) # unicode

            key = path_join(bucket_name, prefix, fname)
            if os.path.isdir(abspath):
                self._new_folder(abspath, key, dirinfo)
                folders.append((self._split_prefix(abspath), abspath))
            else:
                self.upload_file(abspath, key, dirinfo)

        will_delete = set_has_synced - set_local

        for del_obj in will_delete:
            if dirinfo[del_obj].isFile:
                self._up_delete_file(self._split_prefix(del_obj), dirinfo)
            else:
                self._up_delete_folder(self._split_prefix(del_obj) + u'/', dirinfo)

        for obj_key, folders_abspath in folders:
            self._up_path_to_bucket(obj_key, folders_abspath)

    def _up_delete_file(self, objkey, dirinfo):
        assert isinstance(objkey, unicode)
        def callback(object):
            abspath = self._abspath(objkey)
            if abspath.endswith('/'):
                abspath = abspath[:-1]

            if dirinfo.has_key(abspath):
                print dirinfo.pop(abspath).fname

        self._api.delete_object(callback, self._bucket.name, objkey)

    def _up_delete_folder(self, objkey, dirinfo):
        assert isinstance(objkey, unicode)
        def callback(bucket):
            #"Content list:(file)"
            for c in bucket.content_list:
                print '_up_delete_file', c.key
                self._up_delete_file(c.key.decode('utf8'), dirinfo)

            #"Prefix list: (folder)"
            for p in bucket.prefix_list:
                print '_up_delete_folder', p
                self._up_delete_folder(p.decode('utf8'), dirinfo)

        self._api.get_bucket(callback, self._bucket.name,
                             objkey
                             )

    def _upload_file(self, path, key, dirinfo):
        logging.info('upload file[%s]' % key)

        prefix = self._split_prefix(path)

        def callback(object):
            dirinfo[path] = FileInfo(path)
            dirinfo.save()

        self._api.put_object_from_file(callback,
            self._bucket.name, prefix, path)

    def upload_file(self, path, key, dirinfo):
        fileinfo = dirinfo.get(path)
        if fileinfo is None:
            return self._upload_file(path, key, dirinfo)

        # 检验文件是否与服务端的一致
        if fileinfo.is_changed():
            md5 = fileutils.md5(path)
            if md5 and fileinfo.md5 != md5:
                logging.info('file[%s] changed,upload for update.' % key)
                return self._upload_file(path, key)
            else:
                # md5 一样，mtime可能变了
                dirinfo[path] = FileInfo(path, md5)
                dirinfo.save()

        logging.info('file not changed [%s]' % key)

    def _new_folder(self, path, key, dirinfo):
        folder = dirinfo.get(path)
        if folder is None:
            print path

            prefix = self._split_prefix(path) + u'/'
            print prefix
            def callback(object):
                print object
                dirinfo[path] = PathInfo(path)

            self._api.put_object_from_string(callback,
                self._bucket.name, prefix, '')
