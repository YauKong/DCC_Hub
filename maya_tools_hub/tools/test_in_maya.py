"""Maya 测试脚本 - 在 Maya Script Editor 中运行此脚本进行测试。

使用方法：
1. 打开 Maya Script Editor
2. 复制此文件内容到 Script Editor
3. 修改 PROJECT_PATH 为你的实际项目路径
4. 运行脚本
"""

import sys
import os

# ========== 配置区域 ==========
# 修改为你的实际项目路径
PROJECT_PATH = r"E:\workspace\cursor_playground\DCC_Hub"
# ==============================

def setup_path():
    """设置项目路径"""
    if PROJECT_PATH not in sys.path:
        sys.path.insert(0, PROJECT_PATH)
        print(f"✓ Added project path: {PROJECT_PATH}")
    else:
        print(f"✓ Project path already in sys.path: {PROJECT_PATH}")

def test_imports():
    """测试基本导入"""
    print("\n=== 测试 1: 基本导入 ===")
    try:
        from hub.app import run
        from hub.dcc.maya_backend import MayaFacade
        from hub.core.qt_import import import_qt
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_qt():
    """测试 Qt 导入"""
    print("\n=== 测试 2: Qt 导入 ===")
    try:
        from hub.core.qt_import import import_qt
        QtWidgets = import_qt()
        print(f"✓ QtWidgets imported: {type(QtWidgets)}")
        print(f"✓ QApplication available: {hasattr(QtWidgets, 'QApplication')}")
        print(f"✓ QWidget available: {hasattr(QtWidgets, 'QWidget')}")
        return True
    except Exception as e:
        print(f"✗ Qt import failed: {e}")
        return False

def test_facade():
    """测试 DCC Facade"""
    print("\n=== 测试 3: DCC Facade ===")
    try:
        from hub.dcc.maya_backend import MayaFacade
        facade = MayaFacade()
        print(f"✓ Facade created: {facade.name}")
        return True
    except Exception as e:
        print(f"✗ Facade test failed: {e}")
        return False

def test_window():
    """测试窗口创建"""
    print("\n=== 测试 4: 窗口创建 ===")
    try:
        from hub.app import run
        result = run()
        print(f"✓ Run completed, returned: {result}")
        print("✓ Window should be visible now")
        return True
    except Exception as e:
        print(f"✗ Window test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("DCC Hub - Maya 测试脚本")
    print("=" * 50)
    
    # 设置路径
    setup_path()
    
    # 运行测试
    results = []
    results.append(("基本导入", test_imports()))
    results.append(("Qt 导入", test_qt()))
    results.append(("DCC Facade", test_facade()))
    results.append(("窗口创建", test_window()))
    
    # 输出结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("=" * 50)
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(r[1] for r in results)
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ 所有测试通过！")
    else:
        print("✗ 部分测试失败，请检查上面的错误信息")
    print("=" * 50)
    
    return all_passed

if __name__ == "__main__":
    main()

