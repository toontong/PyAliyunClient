#coding:utf8
#TooNTonG 2012-08-28
import os
import wx

class KeyEntryDialog(wx.Dialog):
    _FILE = '.ackey'
    def __init__(
            self, parent, ID, title, size = wx.DefaultSize, pos = wx.DefaultPosition,
            style = wx.DEFAULT_DIALOG_STYLE,
            ):

        # Instead of calling wx.Dialog.__init__ we precreate the dialog
        # so we can set an extra style that must be set before
        # creation, and then we create the GUI object using the Create
        # method.
        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)

        # This next step is the most important, it turns this Python
        # object into the real wrapper of the dialog (instead of pre)
        # as far as the wxPython extension is concerned.
        self.PostCreate(pre)

        # Now continue with the normal construction of the dialog
        # contents
        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self, -1, u"Aliyun.com OSS 连接信息")
        sizer.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, "Access_id:")
        label.SetHelpText("access_id like 'nf2vweubkp3wczejft46s5q4'")
        box.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)

        self.access_id = text = wx.TextCtrl(self, -1, "", size = (180, -1))
        text.SetHelpText("access_id like 'nf2vweubkp3wczejft46s5q4'")
        box.Add(text, 1, wx.ALIGN_CENTRE | wx.ALL, 5)

        sizer.Add(box, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, "Access_key:")
        label.SetHelpText("secret_access_key like '24Z0v2ac9a2bZTMHdS2w2HbcNvI='")
        box.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)

        self.access_key = text = wx.TextCtrl(self, -1, "", size = (180, -1))
        text.SetHelpText(label.GetHelpText())
        box.Add(text, 1, wx.ALIGN_CENTRE | wx.ALL, 5)

        sizer.Add(box, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, "Default Host:")
        label.SetHelpText("Default host is storage.aliyun.com")
        box.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)

        self.host = text = wx.TextCtrl(self, -1, "", size = (180, -1))
        text.SetHelpText(label.GetHelpText())
        text.SetValue("storage.aliyun.com")
        box.Add(text, 1, wx.ALIGN_CENTRE | wx.ALL, 5)

        sizer.Add(box, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.chk_save = wx.CheckBox(self, -1, u"保存验证信息 -- (简单加密保存为本地文件)")
        self.chk_save.SetValue(True)

        sizer.Add(self.chk_save, 0, wx.GROW | wx.LEFT, 10)

        line = wx.StaticLine(self, -1, size = (20, -1), style = wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.TOP, 5)

        btnsizer = wx.StdDialogButtonSizer()

        if wx.Platform != "__WXMSW__":
            btn = wx.ContextHelpButton(self)
            btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_OK)
        btn.SetHelpText("The OK button completes the dialog")
        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_CANCEL)
        btn.SetHelpText("The Cancel button cancels the dialog. (Cool, huh?)")
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTRE_HORIZONTAL | wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)
        self.Center()

    def get_Key(self):
        if os.path.exists(self._FILE):
            fp = open(self._FILE, 'rb')
            data = fp.read()
            dl = data.split('#')
            if len(dl) == 3 and dl[0] and dl[1] and dl[2]:
                return dl

        self.ShowModal()

        host = self.host.GetValue().encode('utf8')
        access_id = self.access_id.GetValue().encode('utf8')
        access_key = self.access_key.GetValue().encode('utf8')

        if self.chk_save.IsChecked():
            fp = open(self._FILE, 'wb+')
            fp.write('#'.join((host, access_id, access_key)))
            fp.close()

        return (host, access_id, access_key)
