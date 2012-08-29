#coding:utf8
#TooNTonG 2012-08-13

import os
import logging

from Tkinter import *

CURRENT_PATH = os.path.dirname(__file__)
APP_NAME = u'ALIYUN.COM OSS GUI Sync Client Tool'

DEBUG = True
if DEBUG:
    logging.info = logging.warning


from Tkinter import *

class Application():

    def __init__(self, master, event_handler):
#        Frame.__init__(self, master)
        self.root = master

        self.createWidgets()
        self.root.pack_slaves()

    def say_hi(self):
        print "hi there, everyone!"

    def createWidgets(self):
        p = PhotoImage(file = os.path.join(CURRENT_PATH, 'logo_aliyun.gif'))
        l = Label(self.root, image = p)
        l.image = p  # 这句不能少，否则图片不显示

        l.pack(side = TOP, anchor = 'nw')


# TODO: 非主线程更新UI，在xp下程序会崩溃
def main(event_handler):
    root = Tk()
    root.geometry('840x570+0+0')
#    root.pack_slaves()
    app = Application(root, event_handler)
    root.mainloop()
#    root.destroy()

if __name__ == '__main__':
    main(None)

