# -*- coding: UTF-8 -*-

'''APP类
'''

import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
print(sys.path)
import wx
from ui import mainframe

# reload(sys)
# sys.setdefaultencoding('utf8')

class WaterInflowPredictorApp(wx.App):
    '''
    '''

    def OnInit(self):
        self.main = mainframe.create(None)
        self.main.Center()
        self.main.Show()

        self.SetTopWindow(self.main)
        return True


def main():
    application = WaterInflowPredictorApp()
    application.MainLoop()


if __name__ == '__main__':
    main()