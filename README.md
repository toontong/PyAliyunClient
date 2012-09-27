PyAliyunClient
==============

* python sync client for aliyun.com OSS  
* run on python2.6
* request wxPython2.9 for GUI
* test on windows7, win7下UI效果比较好，对xp支持不友好 

已调用API：
-------
    手动同步
    Service: list, list_acl
    Bucket: Get，Put，
    Object: Put, Get, Delete, Delete Multiple 
    # 注：Put操作中对HTTP header的操作未实现
  
    Multiple Upload: None
    Object Group: None
    防盗链设置：貌似2012-08月的API中没相关接口提供，

通过对Bucket与Object的操作，实现了与本地文件系统的同步功能

实现功能：
-------
    对各bucket的浏览
    创建bucket，删除空bucket
    head Object
    下行同步增加文件夹、文件与文件的下更新
    上行同步对文件夹、文件的增加与改变、删除 
   
TODO：
-------
    下行同步删除
    对绑定目录的自动同步, 叠加图标
    使用pyinstaller打包成exe文件
    冲突文件让用户选择

