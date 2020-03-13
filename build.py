# -*- coding: UTF-8 -*-

'''打包成可执行文件
'''

import os
import sys


def main(version):
    version_items = version.split('.')
    for i in range(len(version_items)):
        version_items[i] = int(version_items[i])

    with open('version.py', 'w') as fp:
        fp.write('version_info=u"%s"' % version)

    if sys.platform == 'win32':
        version_file_path = 'version_file.txt'
        with open(os.path.join('res', 'file_version_info.txt'), 'r') as fp:
            text = fp.read()
            text = text % {'main_ver': version_items[0],
                           'sub_ver': version_items[1],
                           'min_ver': version_items[2],
                           'build_num': version_items[3] if len(version_items) > 3 else 0
                           }
        with open(version_file_path, 'w') as fp:
            fp.write(text)
        cmdline = 'pyinstaller -F -w ui/app.py -n WaterInflowPredictor_v%s -i res/meilaoban.ico --hidden-import sklearn.neighbors.typedefs ' \
                  '--version-file %s' % (version, version_file_path)
    else:
        cmdline = 'pyinstaller -F -w ui/app.py -n WaterInflowPredictor -i res/meilaoban.icns '

    os.system(cmdline)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python build.py versions')
        exit()
    main(sys.argv[1])