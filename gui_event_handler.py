#coding:utf8
#TooNTonG 2012-08-15
import os
import logging

from sync import DownBucketWorker, UpBucketWorker

class GUIEventHandler(object):
    def __init__(self, aliyun):
        self.aliyun = aliyun
        self.gui = None

        self.current_bucket = ''
        self.current_prefix = ''
        self.current_marker = ''
        self.current_maxkey = ''
        self.current_path = ''
        self.prev_path = ''
        self.delimiter = r'/'

        self._is_down_syncing = False

    # 以下功能辅助函数
    def _call_get_bucket(self):
        self.aliyun.get_bucket(self._callback_get_bucket, self.current_bucket,
            self.current_prefix, self.current_marker, self.delimiter,
            self.current_maxkey)

    def _callback_get_bucket(self, bucket):
        self.gui.set_bucket(bucket, self.current_path)

    # 以下为界面事件
    def on_init_gui(self, host, access_id, access_key):
        self.aliyun.set_key(host, access_id, access_key)
        self.aliyun.get_service(self.gui.set_service)

    def create_bucket(self, bucket, is_private):
        "acl: public-read-write，public-read ，private"
        self.aliyun.create_bucket(
            lambda ret: self.aliyun.get_service(self.gui.set_service),
            bucket,
            'private' if is_private else 'public-read')

    def delete_bucket(self, bucket):
        self.aliyun.delete_bucket(
            lambda ret: self.aliyun.get_service(self.gui.set_service),
            bucket)

    def on_bucket_selected(self, event):
        """选 择左侧bucket事件"""
        self.current_bucket = self.gui.get_bucket_txt(event.m_itemIndex)
        self.current_prefix = ''
        self.prev_path = ''
        self.current_path = ''

        self._call_get_bucket()
        self.aliyun.get_bucket_acl(self.gui.set_bucket_acl, self.current_bucket)

    def on_object_activated(self, event):
        """双击文件/文件夹事件"""
        # path is utf8
        path = self.gui.get_list_obj_txt(event.m_itemIndex)
        if path == '..':
            self.current_path = self.prev_path
            self.prev_path = os.path.basename(self.current_path)
        elif not path.endswith(r'/'):
            logging.info("Click type was file [%s]" % path)
            # save_file is unicode
            save_file = self.gui.show_save_dialog(os.path.basename(path))
            if save_file:
                self.aliyun.get_object_to_file(lambda e:e,
                                         self.current_bucket,
                                         path,
                                         save_file)
            return
        else:
            self.prev_path = self.current_path
            self.current_path = self.prev_path + path

        self.current_prefix = self.current_path
        self._call_get_bucket()

    def on_button_sync_up(self, event):
        '''上行同步按钮'''
        # return utf8, convert to unicode
        self.aliyun.get_service(self._callback_sync_up)

    def on_button_sync_down(self, event):
        '''下行同步按钮'''
        self.aliyun.get_service(self._callback_sync_down)

    def _callback_sync_up(self, service):
        if self._is_down_syncing:
            logging.warning('someone syncing...sync_up return')
            return
        self._is_down_syncing = True

        path = self.gui.get_sync_path().decode('utf8')
        if not os.path.exists(path):
            self._is_down_syncing = False
            logging.warning("up,path [%s] not exists" % path)
            return self.gui.show_msg('目录不存在，上行同步中止!')

        for bucket in service.get_buckets():
            try:
                UpBucketWorker(self.aliyun, path, bucket).run()
            except:
                self._is_down_syncing = False
                raise
        self._is_down_syncing = False

    def _callback_sync_down(self, service):
        if self._is_down_syncing:
            logging.warning('someone syncing...sync_down return')
            return
        self._is_down_syncing = True

        # return utf8, convert to unicode
        path = self.gui.get_sync_path().decode('utf8')
        if not os.path.exists(path):
            self._is_down_syncing = False
            logging.warning("do,path [%s] not exists" % path)
            return self.gui.show_msg('目录不存在，下行同步中止!')

        if os.path.lexists(path):
            logging.warning(u"the path[%s] has some file." % path)

        for bucket in service.get_buckets():
            try:
                DownBucketWorker(self.aliyun, path, bucket).run()
            except:
                self._is_down_syncing = False
                raise

        self._is_down_syncing = False


