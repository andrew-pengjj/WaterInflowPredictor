# -*- coding: UTF-8 -*-

'''日志模块
'''

import os, sys
import logging


class Log(object):
    '''
    '''
    logger = None
    log_name = 'WaterInflowPredictor'

    @staticmethod
    def gen_log_path():
        '''生成log存放路径
        '''
        if hasattr(sys, 'frozen'):
            dir_root = os.path.dirname(os.path.join(os.sys.executable))
        else:
            dir_root = os.path.dirname(os.path.abspath(__file__))
        log_name = '%s.log' % (Log.log_name)
        return os.path.join(dir_root, log_name)

    @staticmethod
    def get_logger():
        if Log.logger == None:
            Log.logger = logging.getLogger(Log.log_name)
            if len(Log.logger.handlers) == 0:
                Log.logger.setLevel(logging.DEBUG)
                # logger.setLevel(logging.INFO)
                # logger.setLevel(logging.WARNING)
                Log.logger.addHandler(logging.StreamHandler(sys.stdout))
                fmt = logging.Formatter('%(asctime)s %(message)s')  # %(filename)s %(funcName)s
                Log.logger.handlers[0].setFormatter(fmt)

                logger_path = Log.gen_log_path()
                file_handler = logging.FileHandler(logger_path)
                fmt = logging.Formatter('%(asctime)s %(levelname)s %(thread)d %(message)s')  # %(filename)s %(funcName)s
                file_handler.setFormatter(fmt)
                Log.logger.addHandler(file_handler)
        return Log.logger

    @staticmethod
    def call(func, tag, *args):
        '''
        '''
        msg = '[%s] %s' % (
        tag, ' '.join([arg.encode('utf8') if isinstance(arg, unicode) else str(arg) for arg in args]))
        func = getattr(Log.get_logger(), func)
        return func(msg)

    @staticmethod
    def d(tag, *args):
        return Log.call('debug', tag, *args)

    @staticmethod
    def i(tag, *args):
        return Log.call('info', tag, *args)

    @staticmethod
    def w(tag, *args):
        return Log.call('warn', tag, *args)

    @staticmethod
    def e(tag, *args):
        return Log.call('error', tag, *args)

    @staticmethod
    def ex(tag, *args):
        return Log.call('exception', tag, *args)