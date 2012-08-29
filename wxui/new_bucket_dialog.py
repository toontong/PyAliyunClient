#coding:utf8
#TooNTonG 2012-08-28
import os
import wx

class NewBucketEntryDialog(wx.Dialog):
    def __init__(
            self, parent, ID = -1, title = u'创建存储空间', size = wx.DefaultSize, pos = wx.DefaultPosition,
            style = wx.DEFAULT_DIALOG_STYLE,
            ):

        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)

        self.PostCreate(pre)

        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self, -1, u"6-16个字符，包括小写字母、数字、下划线(_)和短横线(-)，\n必须以小写字母或者数字开头，不含空格")
        sizer.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, "空间命名:")
        box.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)

        self.bucket_name = text = wx.TextCtrl(self, -1, "", size = (180, -1))
        box.Add(text, 1, wx.ALIGN_CENTRE | wx.ALL, 5)

        sizer.Add(box, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, u" 权  限  :")
        box.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)

        radio1 = self._private = wx.RadioButton(self, -1, u" 私有读写 ", style = wx.RB_GROUP)
        radio2 = self._public = wx.RadioButton(self, -1, u" 公有读 ")

        box.Add(radio1, 1, wx.ALIGN_CENTRE | wx.ALL, 5)
        box.Add(radio2, 1, wx.ALIGN_LEFT | wx.ALL, 5)

        sizer.Add(box, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        line = wx.StaticLine(self, -1, size = (20, -1), style = wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.TOP, 5)

        btnsizer = wx.StdDialogButtonSizer()

        if wx.Platform != "__WXMSW__":
            btn = wx.ContextHelpButton(self)
            btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_OK, u' 确 定 ')
        btn.SetHelpText("The OK button completes the dialog")
        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_CANCEL, u' 取 消 ')
        btn.SetHelpText("The Cancel button cancels the dialog. (Cool, huh?)")
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTRE_HORIZONTAL | wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)
        self.Center()
        self.Bind(wx.EVT_BUTTON, self.on_ok, id = wx.ID_OK)

    def get_bucket_name(self):
        bucket_name = self.bucket_name.GetValue().encode('utf8')
        if len(bucket_name) < 6 or len(bucket_name) > 16:
            return False
        frist = bucket_name[0]
        if not (frist.islower() or frist.isdigit()):
            return False
        for ch in bucket_name:
            if not (ch.islower() or ch == '-' or ch == '_' or ch.isdigit()):
                return False
        return bucket_name

    def on_ok(self, evt):
        bucket_name = self.get_bucket_name()

        if bucket_name:
            evt.Skip()
            return True
        return False

    def get_Key(self):
        "6-16个字符，包括小写字母、数字、下划线(_)和短横线(-)，必须以小写字母或者数字开头，不含空格"
        self.ShowModal()
        bucket_name = self.get_bucket_name()
        bucket_atrr = self._private.GetValue()
        return bucket_name, bucket_atrr


