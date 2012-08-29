#coding:utf8
#TooNTonG 2012-08-13

import logging
from ossapi.oss_xml_handler import (
    ErrorXml,
    GetServiceXml,
    GetBucketXml,
    GetBucketAclXml,
    GetObject
    )
from ossapi.oss_api import OssAPI
from asynccall import AsyncCall, Callable

class _ResultAdapter(object):
    def __init__(self, name, callable, result):
        self.name = name
        self.callable = callable
        self.result = result

    def __call__(self, *args):
        res = self.callable(*args)

        if res.status / 100 != 2:
            e = ErrorXml(res.read())
            logging.error('%s - %s - %s' % (self.name, res.status, e.msg))
            return

        return self.result(res.read())

class AliyunOSS():
    def __init__(self, host = None, access_id = None, secret_access_key = None):
        '''
        args like:
            host = "storage.aliyun.com"
            access_id = "nf0vweubkp3wozejft46l5m4"
            secret_access_key = "64Z0v2Bc9asbZTMHVS2wFHbKNvI="
        '''

        self.set_key(host, access_id, secret_access_key)
        self._async = AsyncCall(logging, threads = 4)

    def set_key(self, host, access_id, secret_access_key):
        self.is_init_key = access_id and secret_access_key
        self._api = OssAPI(host, access_id, secret_access_key)

    def _exceptHandler(self, e):
        import traceback
        traceback.print_exc()

    def get_service(self, callback):
        adapter = _ResultAdapter("GetService",
                                 self._api.get_service,
                                 GetServiceXml)
        callable = Callable(adapter, None,
                            resultHandler = callback,
                            exceptHandler = self._exceptHandler)
        logging.info('Calling GetService')
        self._async.add(callable)

    def get_bucket(self, callback, bucket,
                   prefix = '', marker = '',
                   delimiter = '', max_key = '',
                   headers = {}):
        '''
        prefix  限定返回的object key必须以prefix作为前缀。
                注意使用prefix查询时，返回的key中仍会包含prefix。 
        max-keys  限定此次返回object的最大数，如果不设定，默认为1000，
                  max-keys取值不能大于1000。 
        marker  设定结果从marker之后按字母排序的第一个开始返回。 
        delimiter 是一个用于对Object名字进行分组的字符。
                  所有名字包含指定的前缀且第一次出现delimiter字符之间的object
                  作为一组元素——CommonPrefixes。
        '''
        adapter = _ResultAdapter("GetBucket",
                         self._api.get_bucket,
                         GetBucketXml)
        callable = Callable(adapter,
                            (bucket, prefix, marker, delimiter, max_key),
                            resultHandler = callback,
                            exceptHandler = self._exceptHandler)
        logging.info('Calling GetBucket [%s-%s]' % (bucket, prefix))
        self._async.add(callable)

    def get_bucket_acl(self, callback, bucket):
        adapter = _ResultAdapter("GetBucketAcl",
                                 self._api.get_bucket_acl,
                                 GetBucketAclXml)
        callable = Callable(adapter,
                            (bucket,),
                            resultHandler = callback,
                            exceptHandler = self._exceptHandler)
        logging.info('Calling GetBucketAcl [%s]' % bucket)
        self._async.add(callable)

    def get_object_to_file(self, callback, bucket, object, filename, headers = {}):
        adapter = _ResultAdapter("GetObject",
                                 self._api.get_object_to_file,
                                 GetObject)
        callable = Callable(adapter,
                            (bucket, object, filename),
                            resultHandler = callback,
                            exceptHandler = self._exceptHandler)
        logging.info('Calling GetObject [%s\%s]' % (bucket, object))
        self._async.add(callable)

    def put_object_from_string(self, callback, bucket, object, input_content,
                               content_type = OssAPI.DefaultContentType, headers = {}):
        adapter = _ResultAdapter("PutObject",
                                 self._api.put_object_from_string,
                                 GetObject)
        callable = Callable(adapter,
                            (bucket, object, input_content, content_type, headers),
                            resultHandler = callback,
                            exceptHandler = self._exceptHandler)
        logging.info('Calling PutObject [%s\%s]' % (bucket, object))
        self._async.add(callable)

    def put_object_from_file(self, callback, bucket, object, filename,
                               content_type = OssAPI.DefaultContentType, headers = {}):
        adapter = _ResultAdapter("PutObject",
                                 self._api.put_object_from_file,
                                 GetObject)
        callable = Callable(adapter,
                            (bucket, object, filename, content_type, headers),
                            resultHandler = callback,
                            exceptHandler = self._exceptHandler)
        logging.info('Calling PutObject [%s\%s]' % (bucket, object))
        self._async.add(callable)
