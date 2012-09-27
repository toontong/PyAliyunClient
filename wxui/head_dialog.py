#coding:utf8
#TooNTonG 2012-09-25
import os
import wx

class HeadDialog(wx.Dialog):
    _FILE = '.ackey.pyc'
    def __init__(
            self, parent, id, title,
            headers = {},
            size = wx.DefaultSize, pos = wx.DefaultPosition,
            style = wx.DEFAULT_DIALOG_STYLE,
            ):
        wx.Dialog.__init__(self, parent, id, title, pos, size, style)
#        pre = wx.PreDialog()
#        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
#        pre.Create(parent, ID, title, pos, size, style)
#        self.PostCreate(pre)

        sizer = wx.BoxSizer(wx.VERTICAL)
        box = wx.FlexGridSizer(len(headers), 2, 10, 10)

        for key, val in headers.iteritems():
            label = wx.StaticText(self, -1, "%s:" % key.decode('utf8'))
            box.Add(label, flag = wx.ALIGN_RIGHT | wx.FIXED_MINSIZE)
            txt = wx.TextCtrl(self, -1, size = (300, 20))
            txt.SetValue(val.decode('utf8'))
            box.Add(txt)

        sizer.Add(box, 0, wx.ALL, 10)
        self.SetSizer(sizer)
        sizer.Fit(self)
        self.Center()
