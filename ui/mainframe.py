# -*- coding: UTF-8 -*-

import wx
import os
import sys

from ui.my_number_validator import MyNumberValidator
from algorithm.plot_figure_ import doubleexp
from utils.workthread import WorkThread
from utils.logger import Log

try:
    from version import version_info
except:
    version_info = u'v1.0.0'


def create(parent):
    return MainFrame(parent)


def log_uncaught_exceptions(ex_cls, ex, tb):
    import traceback
    err_msg = ''.join(traceback.format_tb(tb))
    msg = ex.message
    if isinstance(msg, unicode): msg = msg.encode('utf8')
    err_msg += msg
    if not isinstance(err_msg, unicode):
        err_msg = err_msg.decode('utf8')
    err_msg += u'\n'
    Log.e('UncaughtException', err_msg)
    dlg = wx.MessageDialog(None, err_msg, u'WaterInflowPredictor出现异常', style=wx.OK | wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()


sys.excepthook = log_uncaught_exceptions

default_size = (1200, 700)


def run_in_main_thread(func):
    '''主线程运行
    '''
    def wrap_func(*args, **kwargs):
        wx.CallAfter(func, *args, **kwargs)
    return wrap_func


ID_PARAM_K = wx.NewId()
ID_PARAM_q = wx.NewId()
ID_PARAM_M = wx.NewId()
ID_PARAM_mu = wx.NewId()
ID_PARAM_H0 = wx.NewId()
ID_PARAM_D = wx.NewId()
ID_PARAM_W = wx.NewId()
ID_PARAM_Hf = wx.NewId()
ID_PARAM_V = wx.NewId()

ID_OUT_PARAM_A = wx.NewId()
ID_OUT_PARAM_B = wx.NewId()
ID_OUT_PARAM_C = wx.NewId()
ID_OUT_PARAM_D = wx.NewId()
ID_OUT_PARAM_K1 = wx.NewId()
ID_OUT_PARAM_K2 = wx.NewId()


class MainFrame(wx.Frame):
    '''MainFrame
    '''
    def __init__(self, parent):
        super(MainFrame, self).__init__(parent, title=u'WaterInflowPredictor ' + version_info,
                                        style=wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX,
                                        size=default_size)
        self.params = {}
        self.param_ctrls = {}
        self.out_ctrls = {}
        self.image = None
        self.init_ctrls()
        self.upload_file_path = None
        self.Center()
        self._work_thread = WorkThread()

    def init_ctrls(self):
        main_panel = wx.Panel(self)
        self.main_panel = main_panel
        _title_font = wx.Font(30, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False)

        self.Bind(wx.EVT_CLOSE, self.on_close)
        vbox = wx.BoxSizer(wx.VERTICAL)

        _title = wx.StaticText(main_panel, label=u'基于多阶动力系统模型的煤矿工作面涌水量预测计算程序', style=wx.ALIGN_CENTER)
        _title.SetFont(_title_font)
        vbox.Add(_title, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=10)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        input_box = wx.BoxSizer(wx.VERTICAL)
        _input_title = wx.StaticText(main_panel, label=u'输入', style=wx.ALIGN_CENTER)
        _io_title_font = wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False)
        _input_title.SetFont(_io_title_font)
        input_box.Add(_input_title, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=5)

        # 添加输入参数表头
        header_box = wx.BoxSizer(wx.HORIZONTAL)
        font = wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False)
        param_st = wx.StaticText(main_panel, label=u'参数', style=wx.ALIGN_CENTER)
        param_st.SetFont(font)
        header_box.Add(param_st, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL)
        symbol_st = wx.StaticText(main_panel, label=u'符号', style=wx.ALIGN_CENTER)
        symbol_st.SetFont(font)
        header_box.Add(symbol_st, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL)
        unit_st = wx.StaticText(main_panel, label=u'单位', style=wx.ALIGN_CENTER)
        unit_st.SetFont(font)
        header_box.Add(unit_st, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL)
        value_st = wx.StaticText(main_panel, label=u'数值', style=wx.ALIGN_CENTER)
        value_st.SetFont(font)
        header_box.Add(value_st, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL)
        input_box.Add(header_box, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=5)

        # 添加输入参数列表
        self.add_param_line(main_panel, input_box, u'渗透系数', u'K', u'm/d', ID_PARAM_K)
        self.add_param_line(main_panel, input_box, u'单位涌水量', u'q', u'l/s.m', ID_PARAM_q)
        self.add_param_line(main_panel, input_box, u'含水层厚度', u'M', u'm', ID_PARAM_M)
        self.add_param_line(main_panel, input_box, u'释水系数', u'μ', u'l', ID_PARAM_mu)
        self.add_param_line(main_panel, input_box, u'含水层残余\n水头高度', u'H', u'm', ID_PARAM_H0)
        self.add_param_line(main_panel, input_box, u'导裂带最大\n初始推采距', u'D', u'm', ID_PARAM_D)
        self.add_param_line(main_panel, input_box, u'预舒放水量', u'W', u'm³', ID_PARAM_W)
        self.add_param_line(main_panel, input_box, u'导裂带发育\n高度', u'Hf', u'm', ID_PARAM_Hf)
        self.add_param_line(main_panel, input_box, u'工作面推采\n速度', u'V', u'm/d', ID_PARAM_V)

        # 添加文件导入行
        file_import_box = wx.BoxSizer(wx.HORIZONTAL)
        import_st = wx.StaticText(main_panel, label=u'实测推采过程涌水数据', style=wx.ALIGN_CENTER)
        import_st.SetFont(font)
        file_import_box.Add(import_st, proportion=1, flag=wx.ALIGN_CENTER | wx.ALL)
        import_btn = wx.Button(main_panel, label=u'文件导入')
        import_btn.Bind(wx.EVT_BUTTON, self.on_file_upload)
        file_import_box.Add(import_btn, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL)
        input_box.Add(file_import_box, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=5)
        hbox2.Add(input_box, proportion=2, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=20)

        # 计算按钮
        cal_btn = wx.Button(main_panel, label=u'计算')
        cal_btn.Bind(wx.EVT_BUTTON, self.on_cal)
        hbox2.Add(cal_btn, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=20)

        # 输出区域
        output_box = wx.BoxSizer(wx.VERTICAL)
        _output_title = wx.StaticText(main_panel, label=u'输出', style=wx.ALIGN_CENTER)
        _output_title.SetFont(_io_title_font)
        output_box.Add(_output_title, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=5)

        _pic_title = wx.StaticText(main_panel, label=u'工作面涌水量曲线', style=wx.ALIGN_CENTER)
        _pic_title.SetFont(font)
        output_box.Add(_pic_title, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=5)

        # 画图
        # path = os.path.join(os.path.abspath(os.curdir), 'result.png')
        self.image = wx.StaticBitmap(main_panel, wx.ID_ANY)
        output_box.Add(self.image, proportion=7)

        # 计算结果
        _result_title = wx.StaticText(main_panel, label=u'工作面涌水量模型参数', style=wx.ALIGN_CENTER)
        _result_title.SetFont(font)
        output_box.Add(_result_title, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=5)
        output_box.Add(self.get_result_param_line(u'峰值水量', u'峰值水量\n走倾比', ID_OUT_PARAM_A, ID_OUT_PARAM_B),
                       proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=5)
        output_box.Add(self.get_result_param_line(u'动态平衡\n水量', u'动态平衡水\n量走倾比', ID_OUT_PARAM_C, ID_OUT_PARAM_D),
                       proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=5)
        output_box.Add(self.get_result_param_line(u'k1', u'k2', ID_OUT_PARAM_K1, ID_OUT_PARAM_K2),
                       proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=5)

        # 版权申明
        _warranty_st = wx.StaticText(main_panel, label=u'©版权所有 All Rights Reserved', style=wx.ALIGN_CENTER)
        warranty_font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, False)
        _warranty_st.SetFont(warranty_font)
        output_box.Add(_warranty_st, proportion=1, flag=wx.ALIGN_CENTER | wx.TOP, border=15)
        hbox2.Add(output_box, proportion=2, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=20)
        vbox.Add(hbox2, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL)

        main_panel.SetSizer(vbox)
        pass

    def add_param_line(self, main_panel, input_box, param_name, param_symbol, param_unit, id):
        '''添加参数行'''
        font = wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False)
        symbol_font = wx.Font(16, wx.DEFAULT, wx.ITALIC, wx.BOLD, False)
        param_box = wx.BoxSizer(wx.HORIZONTAL)
        param_st = wx.StaticText(main_panel, label=param_name, style=wx.ALIGN_CENTER)
        param_st.SetFont(font)
        param_box.Add(param_st, proportion=1, flag=wx.ALIGN_CENTER | wx.ALL)
        symbol_st = wx.StaticText(main_panel, label=param_symbol, style=wx.ALIGN_CENTER)
        symbol_st.SetFont(symbol_font)
        param_box.Add(symbol_st, proportion=1, flag=wx.ALIGN_CENTER | wx.ALL)
        unit_st = wx.StaticText(main_panel, label=param_unit, style=wx.ALIGN_CENTER)
        unit_st.SetFont(font)
        param_box.Add(unit_st, proportion=1, flag=wx.ALIGN_CENTER | wx.ALL)
        value_input = wx.TextCtrl(main_panel, id, validator=MyNumberValidator())
        self.param_ctrls[str(id)] = value_input
        value_input.Bind(wx.EVT_TEXT, self.on_param_changed)
        param_box.Add(value_input, proportion=1, flag=wx.ALIGN_CENTER | wx.ALL)
        input_box.Add(param_box, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=5)

    def get_result_param_box(self, param_name, id):
        '''构造模型参数控件
        '''
        param_box = wx.BoxSizer(wx.HORIZONTAL)
        font = wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False)
        param_st = wx.StaticText(self.main_panel, label=param_name, style=wx.ALIGN_CENTER)
        param_st.SetFont(font)
        param_box.Add(param_st, proportion=1, flag=wx.ALIGN_CENTER | wx.ALL)

        value_output = wx.TextCtrl(self.main_panel)
        value_output.Enable(False)
        self.out_ctrls[str(id)] = value_output
        param_box.Add(value_output, proportion=1, flag=wx.ALIGN_CENTER | wx.ALL)

        return param_box

    def get_result_param_line(self, param_name1, param_name2, id1, id2):
        param_line_box = wx.BoxSizer(wx.HORIZONTAL)
        param_line_box.Add(self.get_result_param_box(param_name1, id1), proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL)
        param_line_box.Add(self.get_result_param_box(param_name2, id2), proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL)
        return param_line_box

    def on_close(self, event):
        '''退出程序
        '''
        import atexit
        atexit._exithandlers = []  # 禁止退出时弹出错误框
        wx.GetApp().ExitMainLoop()
        event.Skip()

    def on_param_changed(self, event):
        '''参数输入变化
        '''
        e_id = event.GetId()
        param_value = self.param_ctrls[str(e_id)].GetValue()
        self.params[str(e_id)] = param_value

    def validate_params(self):
        '''检查输入是否合法
        '''
        if not len(self.params) == 9:
            dlg = wx.MessageDialog(self, u'未输入全部参数，将使用默认初始值计算！', u'提示', style=wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        for k,v in self.params.items():
            try:
                float_value = float(v)
                self.params[k] = float_value
            except:
                dlg = wx.MessageDialog(self, u'输入参数不合法，将使用默认初始值计算！', u'提示', style=wx.OK | wx.ICON_WARNING)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        return True

    def on_cal(self, event):
        '''响应计算按钮
        '''
        is_param_valid = self.validate_params()
        self._work_thread.post_task(self._cal_task, is_param_valid)
        # if self.upload_file_path:
        #     is_param_valid = self.validate_params()
        #     self._work_thread.post_task(self._cal_task, is_param_valid)
        # else:
        #     if self.validate_params():
        #         self._work_thread.post_task(self._cal_task, True)
        #     else:
        #         dlg = wx.MessageDialog(self, u'请选择导入文件或填写完整参数！', u'提示', style=wx.OK | wx.ICON_ERROR)
        #         dlg.ShowModal()
        #         dlg.Destroy()


    def on_file_upload(self, event):
        '''处理上传文件按钮点击
        '''
        wildcard = 'CSV files (*.csv)|*.csv'
        dlg = wx.FileDialog(self.main_panel, '选择csv文件上传', wildcard=wildcard, style= wx.FD_FILE_MUST_EXIST | wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.upload_file_path = dlg.GetPath()
        dlg.Destroy()

    @run_in_main_thread
    def _set_image(self):
        '''设置图片
        '''
        path = os.path.join(os.path.abspath(os.curdir), 'result.png')
        self.image.SetBitmap(wx.Bitmap(path, wx.BITMAP_TYPE_ANY))
        self.image.Refresh()
        self.image.Show()

    @run_in_main_thread
    def _set_model_params(self, A, B, C, D, K1, K2):
        '''设置模型参数
        '''
        self.out_ctrls[str(ID_OUT_PARAM_A)].SetValue(str(A))
        self.out_ctrls[str(ID_OUT_PARAM_B)].SetValue(str(B))
        self.out_ctrls[str(ID_OUT_PARAM_C)].SetValue(str(C))
        self.out_ctrls[str(ID_OUT_PARAM_D)].SetValue(str(D))
        self.out_ctrls[str(ID_OUT_PARAM_K1)].SetValue(str(K1))
        self.out_ctrls[str(ID_OUT_PARAM_K2)].SetValue(str(K2))

    def _cal_task(self, is_param_valid):
        '''计算任务
        '''
        H = self.params[str(ID_PARAM_H0)] if is_param_valid else 300
        M = self.params[str(ID_PARAM_M)] if is_param_valid else 55
        mu = self.params[str(ID_PARAM_mu)] if is_param_valid else 0.01
        q = self.params[str(ID_PARAM_q)] if is_param_valid else 0.12
        W = self.params[str(ID_PARAM_W)] if is_param_valid else 0.88
        Hf = self.params[str(ID_PARAM_Hf)] if is_param_valid else 64
        K = self.params[str(ID_PARAM_K)] if is_param_valid else 0.1
        D = self.params[str(ID_PARAM_D)] if is_param_valid else 400
        V = self.params[str(ID_PARAM_V)] if is_param_valid else 2.72
        path = os.path.join(os.path.abspath(os.curdir), 'result.png')
        deobj = doubleexp(self.upload_file_path)
        ret, para_dict, keyvalue_dict = deobj.plot_dexp_data(H, M, K, mu, q, W, Hf, D, V, path)
        self._set_model_params(keyvalue_dict['high_volume'], keyvalue_dict['high_ratio'],
                               keyvalue_dict['balance_volume'], keyvalue_dict['balance_ratio'], para_dict['k1'], para_dict['k2'])
        self._set_image()
