#coding:utf8
#TooNTonG 2012-08-13

from wxui import main_dialog as ui
from gui_event_handler import GUIEventHandler
from aliyunoss import AliyunOSS

"""
本程序实现了：
  Bucket: Get，Put，
  Object: Put, Get, Delete, Delete Multiple 
          # 注：Put操作中对HTTP header的添加未实现
  
  Multiple Upload: None
  Object Group: None
  防盗链设置：貌似API中没相关接口提供，

通过对Bucket与Object的操作，实现了与本地文件系统的同步功能
"""

def main():
    host = "storage.aliyun.com"
    access_id = None
    secret_access_key = None
    aliyun = AliyunOSS(host, access_id, secret_access_key)

    event_handler = GUIEventHandler(aliyun)
    ui.main(event_handler)



if __name__ == '__main__':
    main()
