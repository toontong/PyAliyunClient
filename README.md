PyAliyunClient
==============
python for aliyun.com OSS sync client

run on python2.6

request wxPython2.9

test on windows7

本程序实现了：
  Bucket: Get，Put，
  Object: Put, Get, Delete, Delete Multiple 
          # 注：Put操作中对HTTP header的添加未实现
  
  Multiple Upload: None
  Object Group: None
  防盗链设置：貌似API中没相关接口提供，

通过对Bucket与Object的操作，实现了与本地文件系统的同步功能
实现了：
   下行同步增加与改变
   上行同步增加与改变、删除 
   
TODO：
   下午同步删除

