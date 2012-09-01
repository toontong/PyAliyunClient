#coding:utf8
#TooNTonG 2012-08-13

import os
import logging
import locale
import wx
from listview import FileList
from treeview import TreeView
from key_entry_dialog import KeyEntryDialog
from new_bucket_dialog import NewBucketEntryDialog

CURRENT_PATH = os.path.dirname(__file__)
APP_NAME = u'ALIYUN.COM OSS GUI Sync Client Tool'

DEBUG = True
if DEBUG:
    logging.info = logging.warning

class MainDialog(wx.Frame):
    ID_SETTING = wx.NewId()
    ID_SYNC_UP = wx.NewId()
    ID_SYNC_DOWN = wx.NewId()
    ID_VIEW_MGR = wx.NewId()
    ID_VIEW_BROWSE = wx.NewId()
    ID_VIEW_SYNC = wx.NewId()
    ID_NEW_BUCKET = wx.NewId()

    def __init__(self, event_handler) :
        super(MainDialog, self).__init__(parent = None,
                                         id = wx.NewId(),
                                         size = (840, 570),
                                         title = APP_NAME)
        self.event_handler = event_handler
        self.event_handler.gui = self

        self.SetMinSize((840, 570))
        self.SetSize((840, 570))
        self.Centre()

        self.CreateStatusBar()

        menuBar = wx.MenuBar()

        menu1 = wx.Menu()
        menu1.Append(self.ID_SETTING, u"设置a&ccess_key", u"Setting the access_id and secret_access_key")
        menu1.Append(self.ID_SYNC_UP, u"上行同步(&U)", u"Sync the file to OSS.")
        menu1.Append(self.ID_SYNC_DOWN, u"下行同步(&D)", u"Sync the file to local folder.")
        menu1.Append(wx.ID_ABOUT, u"打开同步目录(&P)", u"Open the sync folder on Explorer")
        menu1.AppendSeparator()
        menu1.Append(wx.ID_ABOUT, u"&About", u"About the Application")
        menu1.Append(wx.ID_CLOSE, u"&Exit", u"Exit this Application")
        menuBar.Append(menu1, u"操作(&O)")

        menu2 = wx.Menu()
        menu2.Append(self.ID_VIEW_SYNC, u'同步(&T)', u'同步OSS文件到指定的文件夹', wx.ITEM_RADIO)
        menu2.Append(self.ID_VIEW_MGR, u'管理(&M)', u'对OSS文件进行管理', wx.ITEM_RADIO)
        menu2.Append(self.ID_VIEW_BROWSE, u'浏览(&L)', u'浏览文件', wx.ITEM_RADIO)
        menuBar.Append(menu2, u"视图(&V)")

        self.SetMenuBar(menuBar)
        self.Bind(wx.EVT_MENU, lambda evt: wx.Exit(), id = wx.ID_CLOSE)

        logo = wx.StaticBitmap(self, -1,
            wx.Bitmap(os.path.join(CURRENT_PATH, 'logo_aliyun.png'),
            wx.BITMAP_TYPE_PNG))

        self._splitter = wx.SplitterWindow(self,
            style = wx.SP_3D | wx.SP_BORDER | wx.SP_LIVE_UPDATE | wx.SP_3DSASH | wx.TAB_TRAVERSAL)
        self._splitter.SetMinimumPaneSize(240)

        # 左边bucket列表
        left = wx.Panel(self._splitter, -1 , style = wx.TAB_TRAVERSAL)
        tbNewBucket = wx.Button(left, self.ID_NEW_BUCKET, u"创建存储空间", (10, 10), (100, 24))
        self._tree = TreeView(left, (0, 40))
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(tbNewBucket, 0, wx.EXPAND | wx.ALL, 5)
        vbox.Add(self._tree, 1, wx.EXPAND | wx.ALL, 0)
        left.SetSizer(vbox)

        # 右边文件列表
        right = wx.Panel(self._splitter, -1 , style = wx.TAB_TRAVERSAL)
        self._bucket_info = BucketInfoPanel(right)
        self._list = FileList(right, wx.DefaultPosition, wx.DefaultSize)
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self._bucket_info, 0, wx.EXPAND | wx.ALL, 0)
        vbox.Add(self._list, 1, wx.EXPAND | wx.ALL, 0)
        right.SetSizer(vbox)

        self._splitter.SplitVertically(left, right, 240)

        self.SetBackgroundColour('#FFFFFF')

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(logo, 0, wx.ALIGN_LEFT , 0)
        vbox.Add(self._splitter, 1, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(vbox)
        self.SetAutoLayout(True)
        self.Fit()

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.event_handler.on_bucket_selected, self._tree)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.event_handler.on_object_activated, self._list)
        self.Bind(wx.EVT_MENU, self.on_view_clicked, id = self.ID_VIEW_MGR)
        self.Bind(wx.EVT_MENU, self.on_view_clicked, id = self.ID_VIEW_BROWSE)
        self.Bind(wx.EVT_MENU, self.on_view_clicked, id = self.ID_VIEW_SYNC)
        self.Bind(wx.EVT_MENU, self.init, id = self.ID_SETTING)
        self.Bind(wx.EVT_MENU, self.on_delete_bucket, id = TreeView.ID_DELETE_BUCKET)
        self.Bind(wx.EVT_BUTTON, self.on_create_bucket, id = self.ID_NEW_BUCKET)

        self.Bind(wx.EVT_BUTTON, self.event_handler.on_button_sync_down,
                  id = BucketInfoPanel.ID_SYNC_DOWN)
        self.Bind(wx.EVT_BUTTON, self.event_handler.on_button_sync_up,
                  id = BucketInfoPanel.ID_SYNC_UP)

        self.set_view(self.ID_VIEW_SYNC)

    def init(self, evt = None):
        key_entry = KeyEntryDialog(self, -1, "Input Access key", size = (750, 400),
                         style = wx.DEFAULT_DIALOG_STYLE)
        host, access_id, access_key = key_entry.get_Key(evt)
        if host and access_id and access_key:
            self.event_handler.on_init_gui(host, access_id, access_key)

    def on_create_bucket(self, evt):
        dlg = NewBucketEntryDialog(self,)
        name, attr = dlg.get_Key()
        if name:
            self.event_handler.create_bucket(name, attr)
        dlg.Destroy()

    def on_delete_bucket(self, evt):
        index = self._tree.GetFirstSelected()
        if index < 0:
            return
        bucket_name = self.get_bucket_txt(index)
        self.event_handler.delete_bucket(bucket_name)

    def on_view_clicked(self, evt):
        id = evt.GetId()
        self.set_view(id)

    def set_view(self, id):
        if id == self.ID_VIEW_MGR:
            self._bucket_info.show_mgr_button(True)
            self._bucket_info.show_sync_button(False)
            self._list.set_view(True)
        elif id == self.ID_VIEW_SYNC:
            self._bucket_info.show_sync_button(True)
            self._bucket_info.show_mgr_button(False)
            self._list.set_view(False)
        elif id == self.ID_VIEW_BROWSE:
            self._bucket_info.show_mgr_button(False)
            self._bucket_info.show_sync_button(False)
            self._list.set_view(False)

        self._bucket_info.Layout()
        self._bucket_info.Refresh()

    def get_sync_path(self):
        return self._bucket_info.get_sync_path()

    def get_bucket_txt(self, index):
        return self._tree.GetItemText(index).encode('utf8')

    def get_list_obj_txt(self, index):
        return self._list.GetItemText(index).encode('utf8')

    def set_service(self, service):
        self._tree.DeleteAllItems()
        if service is None:return
        for bucket in service.get_buckets():
            self._tree.add_bucket(bucket)

    def set_bucket(self, bucket, perfix):
        # 选择bucket或双击文件夹，返回数据接口
        self._bucket_info.set_bucket(bucket.name)
        self._bucket_info.set_path(bucket.prefix)
        self._list.set_bucket(bucket, perfix)

    def set_bucket_acl(self, bucket):
        #TODO: 可能不一致
        self._bucket_info.set_grant(bucket.grant)

    def ask_continue(self, msg):
        #　TODO：非main线程，xp下会崩溃
        return wx.ID_YES == wx.MessageDialog(self, msg.decode('utf8'),
            u"是否继续？", wx.YES_NO | wx.ICON_QUESTION).ShowModal()

    def show_msg(self, msg):
        #　TODO：非main线程，xp下会崩溃
        return wx.MessageDialog(self, msg.decode('utf8'),
            self.GetTitle(), wx.OK | wx.ICON_INFORMATION).ShowModal()

    def show_save_dialog(self, filename):
        '''return abs unicode path'''
        dlg = wx.FileDialog(
            self, message = "Save file as ...", defaultDir = os.getcwd(),
            defaultFile = filename, style = wx.SAVE
            )

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if os.path.exists(path) and self.ask_continue("文件已存在，将覆盖已有文件，是否断续？"):
                return path
        return None

class BucketInfoPanel(wx.Panel):
    ID_DELETE = wx.NewId()
    ID_FODLER = wx.NewId()
    ID_FILE = wx.NewId()
    ID_SYNC_UP = wx.NewId()
    ID_SYNC_DOWN = wx.NewId()

    def __init__(self, parent, pos = wx.DefaultPosition, size = wx.DefaultSize):
        wx.Panel.__init__(self, parent, -1, pos, size = (-1, 70))

        self.bucket_name = wx.StaticText(self, -1, u"")
        self.bucket_atrr = wx.StaticText(self, -1, u"")
        self.current_path = wx.StaticText(self, -1, u"当前目录")

        txt_path = wx.StaticText(self, -1, u"同步目录：")
        self.sync_path = edit_path = wx.TextCtrl(self, -1, u'未选择', size = (60, 25), style = wx.TE_READONLY)#; edit_path.Disable()
        bt_select = wx.Button(self, -1, u'选择目录', size = (60, 25))
        bt_sync_up = wx.Button(self, self.ID_SYNC_UP, u'上行同步', size = (60, 25))
        bt_sync_down = wx.Button(self, self.ID_SYNC_DOWN, u'下行同步', size = (60, 25))

        self.sync_box = wx.BoxSizer()
        self.sync_box.Add(txt_path, 0, wx.EXPAND | wx.LEFT | wx.TOP, 5)
        self.sync_box.Add(edit_path, 1, wx.EXPAND, 0)
        self.sync_box.Add(bt_select, 0, wx.EXPAND, 0)
        self.sync_box.Add(bt_sync_up, 0, wx.EXPAND, 0)
        self.sync_box.Add(bt_sync_down, 0, wx.EXPAND, 0)

        if DEBUG:edit_path.SetLabelText(u"F:\\新建文件夹")

        line = wx.StaticLine(self, style = wx.LI_VERTICAL)

        self.bt_delete = wx.wx.Button(self, self.ID_DELETE, u"删 除", size = (60, 25), style = wx.NO_BORDER)
        self.bt_new_Folder = wx.wx.Button(self, self.ID_FODLER, u"新建文件夹", size = (80, 25), style = wx.NO_BORDER)
        self.bt_new_File = wx.wx.Button(self, self.ID_FILE, u"上传文件", size = (60, 25), style = wx.NO_BORDER)

        hbox1 = wx.BoxSizer()
        hbox1.Add(self.bucket_name, 1, wx.EXPAND | wx.LEFT | wx.TOP, 5)
        hbox1.Add(self.bucket_atrr, 0, wx.ALIGN_RIGHT | wx.TOP | wx.RIGHT, 5)

        self.info_box = hbox2 = wx.BoxSizer()
        hbox2.Add(self.current_path, 1, wx.EXPAND | wx.ALL, 5)
        hbox2.Add(self.bt_new_Folder, 0, wx.ALIGN_RIGHT, 0)
        hbox2.Add(self.bt_new_File, 0, wx.ALIGN_RIGHT, 0)
        hbox2.Add(self.bt_delete, 0, wx.ALIGN_RIGHT, 0)

        vbox = wx.BoxSizer(wx.VERTICAL)

        vbox.Add(hbox1, 0, wx.EXPAND | wx.ALL, 5)
        vbox.Add(line, 0, wx.EXPAND | wx.DOWN, 5)
        vbox.Add(hbox2, 1, wx.EXPAND | wx.DOWN | wx.RIGHT, 5)
        vbox.Add(self.sync_box, 1, wx.EXPAND | wx.DOWN | wx.RIGHT, 5)
        self.SetSizer(vbox)
        self.SetAutoLayout(True)

        self.Bind(wx.EVT_BUTTON, self._on_chioce_dir, bt_select)

    def show_sync_button(self, show = True):
        [self.sync_box.GetItem(i).Show(show) for i in range(self.sync_box.GetItemCount())]
        self.current_path.Show(not show)
        self.bt_new_Folder.Show(not show)
        self.bt_new_File.Show(not show)

    def show_mgr_button(self, show = True):
        self.bt_delete.Show(show)
        self.bt_new_Folder.Show(show)
        self.bt_new_File.Show(show)

    def set_path(self, path):
        if not path:
            path = '顶层目录'
        self.current_path.SetLabelText(u'当前：%s' % path.decode('utf8'))

    def set_bucket(self, name):
        self.bucket_name.SetLabelText(name.decode('utf8'))

    def set_grant(self, grant):
        grant = {'public-read':u'公共读权限', 'private': u'私有权限'}.get(grant, u'私有权限')
        self.bucket_atrr.SetLabelText(u"读写权限：%s" % grant)
        self.Layout()
        self.Refresh()

    def get_sync_path(self):
        return self.sync_path.GetLabelText().encode('utf8')

    def _on_chioce_dir(self, evt):
        dlg = wx.DirDialog(self, u"^_^选择一个文件夹作为同步目录(建议为空文件夹):",
                           r'c:/',
                          style = wx.DD_DEFAULT_STYLE
#                          | wx.DD_DIR_MUST_EXIST
                          | wx.DD_CHANGE_DIR)

        while dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if os.listdir(path) and \
                 wx.ID_YES != wx.MessageDialog(self, u"目录非空，是否继续？",
                                          u"是否继续？", wx.YES_NO).ShowModal():
                    continue
            self.sync_path.SetLabelText(path)
            break

        dlg.Destroy()

# TODO: 非主线程更新UI，在xp下程序会崩溃
def main(event_handler):
    class Application(wx.App):
        def OnInit(self):
            locale.setlocale(locale.LC_ALL, 'english')
            win = MainDialog(event_handler)
            win.init()
            win.Show()
            return True

    Application().MainLoop()

if __name__ == '__main__':
    main(None)
