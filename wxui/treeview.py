#coding:utf8
#TooNTonG 2012-08-13
import sys
import wx
import wx.lib.mixins.listctrl  as  listmix

class TreeView(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    ID_DELETE_BUCKET = wx.NewId()
    def __init__(self, parent, pos = wx.DefaultPosition,
                 size = wx.DefaultSize, style = wx.LC_REPORT
                                 #| wx.BORDER_SUNKEN
                                 | wx.BORDER_NONE
                                 | wx.LC_EDIT_LABELS
                                 | wx.LC_SORT_ASCENDING):
        wx.ListCtrl.__init__(self, parent, -1, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

        isz = (16, 16)
        il = wx.ImageList(isz[0], isz[1])
        self.fldridx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, isz))
        self.fldropenidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER_OPEN, wx.ART_OTHER, isz))
#        fileidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz))

        self.SetImageList(il, wx.IMAGE_LIST_SMALL)
        # self.InsertColumn(0, 'Bucket Name')

        info = wx.ListItem()
        info.m_mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
        info.m_image = -1
        info.m_format = 0
        info.m_text = 'Bucket Name'
        self.InsertColumnInfo(0, info)

        self.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.on_right_clicked)

    def on_right_clicked(self, evt):
        menu = wx.Menu()
        menu.Append(self.ID_DELETE_BUCKET, u'删除')
        self.PopupMenu(menu)
        menu.Destroy()

    def add_bucket(self, bucket):
        # TODO: 非主线程更新UI，在xp下程序会崩溃
        self.InsertImageStringItem(sys.maxint, bucket.name, self.fldridx)
        return
        child = self.AppendItem(self.root, bucket.name)
        self.SetPyData(child, bucket)
        self.SetItemImage(child, self.fldridx, wx.TreeItemIcon_Normal)
        self.SetItemImage(child, self.fldropenidx, wx.TreeItemIcon_Expanded)
        self.ExpandAll()
