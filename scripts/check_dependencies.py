#!/usr/bin/env python3
"""
依赖检查脚本

检查所有必需的依赖项是否正确安装。
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Tuple

# 颜色输出
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(msg: str):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{msg:^60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}\n")

def print_success(msg: str):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg: str):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def check_python_version() -> Tuple[bool, str]:
    """检查Python版本"""
    version = sys.version_info
    required = (3, 11)
    
    if version >= required:
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    else:
        return False, f"需要 Python {required[0]}.{required[1]}+，当前 {version.major}.{version.minor}.{version.micro}"

def check_pip_package(package: str) -> Tuple[bool, str]:
    """检查pip包是否安装"""
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'show', package],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # 提取版本号
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    version = line.split(':', 1)[1].strip()
                    return True, f"{package} ({version})"
            return True, package
        else:
            return False, package
    except Exception as e:
        return False, f"{package} (检查失败: {e})"

def check_file_exists(filepath: str) -> Tuple[bool, str]:
    """检查文件是否存在"""
    path = Path(filepath)
    if path.exists():
        return True, filepath
    else:
        return False, f"{filepath} (不存在)"

def check_env_variables() -> List[Tuple[bool, str]]:
    """检查环境变量"""
    import os
    results = []
    
    # 必需的环境变量
    required = {
        'ZHIPUAI_API_KEY': False,  # 必需但不验证值
        'DB_ENCRYPTION_KEY': False,
    }
    
    # 可选的环境变量
    optional = {
        'TUSHARE_TOKEN': False,
        'SECRET_KEY': False,
    }
    
    for var in required:
        value = os.environ.get(var)
        if value and value != f'your_{var.lower()}_here':
            results.append((True, f"{var} = ***已设置***"))
        else:
            results.append((False, f"{var} = 未设置或使用默认值"))
    
    for var in optional:
        value = os.environ.get(var)
        if value:
            results.append((True, f"{var} = ***已设置*** (可选)"))
        else:
            results.append((True, f"{var} = 未设置 (可选)"))
    
    return results

def main():
    """主检查流程"""
    print_header("WisTrade 依赖检查工具")
    
    # 1. Python版本
    print(f"{Colors.BOLD}[1/6] 检查Python版本{Colors.END}")
    success, msg = check_python_version()
    if success:
        print_success(msg)
    else:
        print_error(msg)
        print_warning("请升级Python到3.11或更高版本")
        sys.exit(1)
    
    # 2. 核心依赖
    print(f"\n{Colors.BOLD}[2/6] 检查核心依赖{Colors.END}")
    core_packages = [
        'PyQt6',
        'pyqtgraph',
        'pandas',
        'numpy',
        'pyyaml',
        'pydantic',
        'aiohttp',
        'httpx',
        'python-dotenv',
    ]
    
    for package in core_packages:
        success, msg = check_pip_package(package)
        if success:
            print_success(msg)
        else:
            print_error(msg)
    
    # 3. AI和数据依赖
    print(f"\n{Colors.BOLD}[3/6] 检查AI和数据依赖{Colors.END}")
    ai_packages = [
        'openai',
        'zhipuai',
        'akshare',
        'tushare',
    ]
    
    for package in ai_packages:
        success, msg = check_pip_package(package)
        if success:
            print_success(msg)
        else:
            print_warning(f"{msg} - 可选依赖")
    
    # 4. 券商依赖
    print(f"\n{Colors.BOLD}[4/6] 检查券商依赖{Colors.END}")
    broker_packages = [
        ('xtquant', 'QMT官方库（实盘必需）'),
        ('easyxt', 'QMT开源替代（可选）'),
    ]
    
    for package, desc in broker_packages:
        success, msg = check_pip_package(package)
        if success:
            print_success(msg)
        else:
            print_warning(f"{package} - {desc}")
    
    # 5. 配置文件
    print(f"\n{Colors.BOLD}[5/6] 检查配置文件{Colors.END}")
    config_files = [
        '.env',
        'config/settings.yaml',
        'requirements.txt',
    ]
    
    for filepath in config_files:
        success, msg = check_file_exists(filepath)
        if success:
            print_success(msg)
        else:
            print_error(msg)
    
    # 6. 环境变量
    print(f"\n{Colors.BOLD}[6/6] 检查环境变量{Colors.END}")
    env_results = check_env_variables()
    for success, msg in env_results:
        if success:
            print_success(msg)
        else:
            print_error(msg)
    
    # 总结
    print_header("检查完成")
    
    print(f"\n{Colors.BOLD}下一步操作:{Colors.END}")
    print("1. 如果缺少依赖，运行: pip install -r requirements.txt")
    print("2. 如果缺少.env，运行: cp .env.example .env")
    print("3. 编辑.env文件，填入API密钥")
    print("4. 启动应用: python -m wistrade.main")
    print()
    
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}检查已取消{Colors.END}")
        sys.exit(1)
