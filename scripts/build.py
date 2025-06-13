import os
import sys
import subprocess
from datetime import datetime

# 设置控制台编码为 UTF-8
if sys.platform.startswith('win'):
    try:
        # 设置控制台代码页为 UTF-8
        subprocess.run(['chcp', '65001'], shell=True, check=True)
    except subprocess.CalledProcessError:
        pass

# 获取项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 切换到项目根目录
os.chdir(ROOT_DIR)

# 设置环境变量
os.environ["NUITKA_C_COMPILER"] = "gcc"

# 设置应用程序名称
APP_NAME = "Language Boy"

# 路径配置
MAIN_SCRIPT = os.path.join(ROOT_DIR, "main.py")
ICON_PATH = os.path.join(ROOT_DIR, "resource", "images","logo.ico")
BUILD_DIR = os.path.join(ROOT_DIR, "build")

# Nuitka 打包配置5
config = [
    sys.executable,
    '-m', 'nuitka',
    '--standalone',
    '--mingw64',
    f'--output-dir={BUILD_DIR}',
    '--lto=yes',
    '--show-scons',
    '--enable-plugin=pyqt6',
    '--jobs=16',
    '--assume-yes-for-download',
    '--onefile',
    '--windows-console-mode=disable',
    f'--output-filename={APP_NAME}.exe',
    f'--windows-icon-from-ico={ICON_PATH}',
    '--nofollow-import-to=numpy,scipy,matplotlib,pyserial,qfluentwidgets',
    '--onefile-tempdir-spec={TEMP}/qt_language_boy',
    '--remove-output',
]
# 添加入口文件
config.append(MAIN_SCRIPT)

def print_project_info():
    """打印项目信息"""
    print(f"Project Root: {ROOT_DIR}")
    print(f"Main Script: {MAIN_SCRIPT}")
    print(f"Icon Path: {ICON_PATH}")
    print(f"Build Directory: {BUILD_DIR}")

try:
    print(f"=== {APP_NAME} Build Script ===")
    print_project_info()
    print("\nStarting build process...")
    start_time = datetime.now()
    
    # 执行打包命令
    result = subprocess.run(config, check=True)
    
    if result.returncode == 0:
        print("\nBuild successful!")
        end_time = datetime.now()
        duration = end_time - start_time
        print(f"Build duration: {duration}")
        
        # 输出文件位置
        exe_path = os.path.join(BUILD_DIR, f"{APP_NAME}.exe")
        if os.path.exists(exe_path):
            print(f"Executable location: {os.path.abspath(exe_path)}")
    else:
        print("\nBuild failed!")

except Exception as e:
    print(f"\nError during build process: {e}") 