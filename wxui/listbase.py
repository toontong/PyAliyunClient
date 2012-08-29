#coding:utf8
#TooNTonG 2012-08-13

import wx

class VirtualList(wx.ListCtrl):
    def __init__(self, parent, columns, editable = False, imgCol = 0,
                 sortor = None, sortImgs = (0, 1), pos = (0, 0), size = (400, 350)):
        self._editable = 0
        if editable:
            self._editable = wx.LC_EDIT_LABELS
        wx.ListCtrl.__init__(self, parent, -1, pos = pos, size = size,
                             style = wx.LC_REPORT | wx.LC_VIRTUAL | self._editable | wx.LC_SINGLE_SEL)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.onColClick)
        self.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.onEndEdit)
        self._col = -1
        self._imgCol = imgCol
        self._dataSource = None
        self.SetItemCount(0)
        self._sortImgs = sortImgs
        self._sortorProxy = sortor
        self._onSort = None

        self.ClearAll()
        self._colSortFlag = []

        for i, col in enumerate(columns):
            self.InsertColumn(i, col)
            self._colSortFlag.append(0)
        self._dataSource = []
        self.SetItemCount(0)
        self.sortColumn(0, 1)

    def _sortor(self, item1, item2):
        if not self._sortorProxy is None:
            return self._sortorProxy(self._col, self._colSortFlag[self._col], item1, item2)
        return 0

    def OnGetItemText(self, item, col):
        if not self._dataSource:
            return ''
        if len(self._dataSource[item]) < col + 1:
            return ''
        return self._dataSource[item][col]

    def OnGetItemImage(self, item):
        if not self._dataSource:
            return None
        if len(self._dataSource) < item + 1:
            return None
        return self._dataSource[item][self._imgCol]

    def setItemData(self, itemId, col, value):
        self._dataSource[itemId][col] = value

    def getItemData(self, itemId):
        return self._dataSource[itemId]

    def removeItem(self, itemId):
        del self._dataSource[itemId]
        self.SetItemCount(len(self._dataSource))
        self.Refresh()

    def iconView(self):
        self.SetWindowStyle(wx.LC_ICON | wx.LC_VIRTUAL | self._editable | wx.LC_SINGLE_SEL)

    def reportView(self):
        self.SetWindowStyle(wx.LC_REPORT | wx.LC_VIRTUAL | self._editable | wx.LC_SINGLE_SEL)

    def appendItem(self, item):
        lastSize = len(self._dataSource)
        self._dataSource.append(item)
        self.SetItemCount(lastSize + 1)
        self.EditLabel(lastSize)

    def sortColumn(self, col, asc = 1):
        oldCol = self._col
        self._col = col
        self._colSortFlag[self._col] = asc
        self._sort()
        self._updateImages(oldCol)
        if self._onSort:
            self._onSort()

    def setOnSortCallback(self, callback):
        self._onSort = callback

    def _sort(self):
        if self._sortor is None:
            return

        self._dataSource.sort(self._sortor)
        self.Refresh()

    def setDataSource(self, columns, source):
        self._dataSource = source
        self.SetItemCount(len(source))
        self.sortColumn(self._col, self._colSortFlag[self._col])

    def reload(self):
        for i in range(0, len(self._colSortFlag)):
            self._colSortFlag[0] = 1
        self.sortColumn(0, 1)

    def _updateImages(self, oldCol):
        sortImages = self._sortImgs
        if self._col != -1 and sortImages[0] != -1:
            img = sortImages[self._colSortFlag[self._col]]
            if oldCol != -1:
                self.ClearColumnImage(oldCol)
            self.SetColumnImage(self._col, img)

    def onColClick(self, event):
        self.sortColumn(event.GetColumn(), int(not self._colSortFlag[self._col]))
        event.Skip()

    def onEndEdit(self, event):
        self._dataSource[event.Item.Id][0] = event.Item.Text
        event.Skip()
