#coding:utf8
#TooNTonG 2012-08-13
import os, time
import logging
import wx
import wx.lib.mixins.listctrl  as  listmix

class FileList(wx.ListCtrl, listmix.CheckListCtrlMixin):
    idx_fname = 0
    idx_size = 1
    idx_type = 2
    idx_modified = 3
    idx_checked = 4
    idx_key = 5
    idx_pyobj = 100 + 1

    def __init__(self, parent, pos, size):
        wx.ListCtrl.__init__(
            self, parent, -1, pos,
            style = wx.LC_REPORT | wx.LC_VIRTUAL | wx.LC_HRULES | wx.LC_VRULES
            )
        listmix.CheckListCtrlMixin.__init__(self)
        self.log = logging

        self.is_checked_model = False
        self.items = []

        isz = (16, 16)
        il = self.il = wx.ImageList(16, 16)
        self.fldridx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, isz))

        self.fileidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz))
        self.imgLsCheck = self.GetImageList(wx.IMAGE_LIST_SMALL)
        self.imgLsFolder = il

        self.InsertColumn(self.idx_fname, u"文件名称")
        self.InsertColumn(self.idx_size, u"大小", wx.LIST_FORMAT_CENTER)
        self.InsertColumn(self.idx_type, u"类型", wx.LIST_FORMAT_CENTER)
        self.InsertColumn(self.idx_modified, u"上传时间(GMT)", wx.LIST_FORMAT_CENTER)
        self.SetColumnWidth(self.idx_fname, 300)
        self.SetColumnWidth(self.idx_size, 80)
        self.SetColumnWidth(self.idx_type, 60)
        self.SetColumnWidth(self.idx_modified, 140)

        self.SetItemCount(len(self.items))

        #self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        #self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)

    def set_view(self, isMgrView):
        self.is_checked_model = isMgrView
        if self.is_checked_model:
            self.SetImageList(self.imgLsCheck, wx.IMAGE_LIST_SMALL)
        else:
            self.SetImageList(self.imgLsFolder, wx.IMAGE_LIST_SMALL)
        self.Refresh()

    def set_bucket(self, bucket, prefix):
        ls = []
        #"Prefix list: (folder)"
        for p in bucket.prefix_list:
            ls.append(self._folder(p, prefix))

        #"Content list:(file)"
        for c in bucket.content_list:
            if prefix and c.key == prefix:
                ls.insert(0, self._folder(c.key, prefix))
            else:
                ls.append(self._file(c, prefix))

        self.items = ls
        self.SetItemCount(len(self.items))
        self.Refresh()

    def _folder(self, o, prefix):
        name = '..' if prefix and o == prefix else o[len(prefix):]
        return {
                self.idx_fname:name.decode('utf8'),
                self.idx_key:o,
                self.idx_type:u'文件夹',
                self.idx_modified:u'-',
                self.idx_size:u'-',
                self.idx_checked: False
                }

    def _file(self, o, prefix):
        name = o.key[len(prefix):]
        return {
            self.idx_fname:name.decode('utf8'),
            self.idx_key: o.key,
            self.idx_size:_size(o.size),
            self.idx_type:os.path.splitext(o.key)[1],
            self.idx_modified:_time(o.last_modified),
            self.idx_checked: False,
            self.idx_pyobj:o,
            }

    def OnItemSelected(self, event):
        self.currentItem = event.m_itemIndex
        self.log.info('OnItemSelected: "%s", "%s", "%s", "%s"\n' %
                           (self.currentItem,
                            self.GetItemText(self.currentItem),
                            self.getColumnText(self.currentItem, 1),
                            self.getColumnText(self.currentItem, 2)))

    def OnItemActivated(self, event):

        if not self.is_checked_model:
            event.Skip()
            return
        o = self.items[event.m_itemIndex]
        o[self.idx_checked] = not o[self.idx_checked]
        self.CheckItem(event.m_itemIndex, o[self.idx_checked])
        self.RefreshItem(event.m_itemIndex)

    def getColumnText(self, index, col):
        item = self.GetItem(index, col)
        return item.GetText()

    def OnItemDeselected(self, evt):
        self.log.info("OnItemDeselected: %s" % evt.m_itemIndex)

    #-----------------------------------------------------------------
    # These methods are callbacks for implementing the "virtualness"
    # of the list...  Normally you would determine the text,
    # attributes and/or image based on values from some external data
    # source, but for this demo we'll just calculate them
    def OnGetItemText(self, item, col):
        if len(self.items) <= item:
            return ""
        try:return self.items[item][col]
        except:return ""

    def OnGetItemImage(self, item):
        if len(self.items) <= item:
            return self.fileidx
        o = self.items[item]

        if self.is_checked_model:
            return o.get(self.idx_checked)

        if o and o.get(self.idx_type) == u'文件夹':
            return self.fldridx
        else:
            return self.fileidx

def _time(gmtime):
    # 是格林威治时间，要加8小时
    # o.last_modified = "2008-09-26T01:51:42.000Z"
    try:return time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(gmtime[:19], "%Y-%m-%dT%H:%M:%S"))
    except:return gmtime

_1T = 2 ** 40
_1G = 2 ** 30
_1M = 2 ** 20
_1K = 2 ** 10
def _size(size):
    size = float(size)
    if size < _1K:
        return '%0.2f B' % (size)
    elif size >= _1T:
        return '%0.2f TB' % (size / _1T)
    elif size >= _1G:
        return '%0.2f GB' % (size / _1G)
    elif size >= _1M:
        return '%0.2f MB' % (size / _1M)
    elif size >= _1K:
        return '%0.2f KB' % (size / _1K)
    else:
        return '%0.2f B' % (size)
