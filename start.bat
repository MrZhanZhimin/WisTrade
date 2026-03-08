@echo off
REM WisTrade 快速启动脚本 (Windows)

setlocal enabledelayedexpansion

REM 项目根目录
cd /d "%~dp0"

echo.
echo ============================================================
echo                  WisTrade 启动脚本
echo             AI-Powered Stock Trading Tool
echo ============================================================
echo.

REM 检查虚拟环境
if not exist "venv" (
    echo [警告] 未找到虚拟环境，正在创建...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo [成功] 虚拟环境已创建
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 检查Python版本
python --version 2>&1 | findstr /R "3\.1[1-9]" >nul
if errorlevel 1 (
    echo [错误] Python版本过低，需要 Python 3.11 或更高版本
    python --version
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [成功] Python版本: %PYTHON_VERSION%

REM 检查依赖
echo 检查依赖...
python -c "import PyQt6" 2>nul
if errorlevel 1 (
    echo [警告] 检测到缺失依赖，正在安装...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
    echo [成功] 依赖已安装
) else (
    echo [成功] 依赖完整
)

REM 检查.env文件
if not exist ".env" (
    echo [警告] 未找到.env文件，从模板创建...
    copy .env.example .env >nul
    echo [成功] .env已创建
    echo.
    echo [重要] 请编辑.env文件，填入您的API密钥:
    echo   - ZHIPUAI_API_KEY (必需)
    echo   - DB_ENCRYPTION_KEY (必需)
    echo   - TUSHARE_TOKEN (可选)
    echo.
    pause
)

REM 创建必要目录
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "config" mkdir config

REM 启动应用
echo.
echo ============================================================
echo               正在启动 WisTrade...
echo ============================================================
echo.

python -m wistrade.main

REM 退出状态
if errorlevel 1 (
    echo.
    echo [错误] WisTrade异常退出
    pause
    exit /b 1
) else (
    echo.
    echo [成功] WisTrade已正常退出
    pause
    exit /b 0
)
