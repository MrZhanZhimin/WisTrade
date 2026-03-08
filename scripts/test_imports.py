#!/usr/bin/env python3
"""
测试WisTrade核心模块导入

这个脚本验证所有核心模块可以正确导入。
"""

import sys
import logging
from pathlib import Path

# 设置路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """测试所有核心模块导入"""
    
    modules_to_test = [
        ("wistrade.core.config", "配置模块"),
        ("wistrade.core.logger", "日志模块"),
        ("wistrade.core.auth", "认证模块"),
        ("wistrade.brokers.base", "券商基类"),
        ("wistrade.ai.llm_client", "AI客户端"),
        ("wistrade.data.market_data", "市场数据"),
        ("wistrade.trading.trading_engine", "交易引擎"),
        ("wistrade.storage.models", "数据模型"),
        ("wistrade.ui.styles", "UI样式"),
    ]
    
    failed = []
    
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            logger.info(f"✓ {description} ({module_name})")
        except Exception as e:
            logger.error(f"✗ {description} ({module_name}): {e}")
            failed.append((module_name, str(e)))
    
    print("\n" + "="*60)
    print(f"测试结果: {len(modules_to_test) - len(failed)}/{len(modules_to_test)} 通过")
    print("="*60 + "\n")
    
    if failed:
        print("失败的模块:")
        for module, error in failed:
            print(f"  - {module}: {error}")
        return 1
    else:
        print("✅ 所有核心模块导入成功!")
        return 0

if __name__ == "__main__":
    sys.exit(test_imports())
