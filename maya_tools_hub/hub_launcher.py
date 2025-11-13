"""Hub launcher - entry point for Maya/3ds Max integration with hot reload support."""
import os
import sys

# Get launcher directory - handle both direct execution and exec() execution
if '__file__' in globals():
    # Normal execution: __file__ exists
    _launcher_dir = os.path.dirname(os.path.abspath(__file__))
else:
    # exec() execution: __file__ doesn't exist, use sys.path to find it
    # Assume DCC_Hub is already in sys.path
    _launcher_dir = None
    for path in sys.path:
        potential_dir = os.path.join(path, "maya_tools_hub")
        if os.path.exists(potential_dir) and os.path.exists(os.path.join(potential_dir, "hub_launcher.py")):
            _launcher_dir = potential_dir
            break
    
    # If still not found, try to infer from current working directory
    if _launcher_dir is None:
        cwd = os.getcwd()
        potential_dir = os.path.join(cwd, "maya_tools_hub")
        if os.path.exists(potential_dir) and os.path.exists(os.path.join(potential_dir, "hub_launcher.py")):
            _launcher_dir = potential_dir
        else:
            # Last resort: assume we're in DCC_Hub/maya_tools_hub
            _launcher_dir = os.path.dirname(os.path.abspath(os.getcwd()))
            if not os.path.exists(os.path.join(_launcher_dir, "hub_launcher.py")):
                raise RuntimeError("Cannot determine hub_launcher.py location. Please ensure DCC_Hub is in sys.path.")

# Add vendor/thirdparty_libs to path FIRST (priority for project dependencies)
_vendor_path = os.path.join(_launcher_dir, "hub", "vendor", "thirdparty_libs")
if os.path.exists(_vendor_path) and _vendor_path not in sys.path:
    sys.path.insert(0, _vendor_path)

# Add project root to Python path
# This allows Maya to import 'hub' and 'Qt' modules
_project_root = os.path.dirname(_launcher_dir)  # DCC_Hub directory
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Also add maya_tools_hub to path so we can import hub directly
_maya_tools_hub_dir = _launcher_dir
if _maya_tools_hub_dir not in sys.path:
    sys.path.insert(0, _maya_tools_hub_dir)


def reload_hub():
    """热重载 hub 模块 - 从 sys.modules 中清除所有 hub 相关模块缓存。
    
    这允许在开发时修改代码后无需重启 Maya 即可看到更改。
    只清除 hub 包及其子模块，保留外部依赖（如 Qt、maya 等）。
    """
    # 找到所有 hub 相关的模块
    modules_to_remove = [
        key for key in list(sys.modules.keys())
        if key.startswith('hub.')
    ]
    
    # 也删除 hub 本身
    if 'hub' in sys.modules:
        modules_to_remove.append('hub')
    
    # 删除模块缓存
    for module_name in modules_to_remove:
        del sys.modules[module_name]
    
    print(f"[Reload] Reloaded {len(modules_to_remove)} hub modules")
    if modules_to_remove:
        print(f"  Removed: {', '.join(modules_to_remove[:5])}{'...' if len(modules_to_remove) > 5 else ''}")


def run_with_reload():
    """运行 Hub 并支持热重载 - 先清除模块缓存再导入运行。"""
    reload_hub()
    from hub.app import run
    return run()


# Now we can import hub modules
from hub.app import run


if __name__ == "__main__":
    # 只有当文件被直接执行（而不是通过 exec()）时才自动运行
    # 通过 exec() 执行时，__file__ 不存在，所以不会自动运行
    if '__file__' in globals():
        # 检查是否有 --reload 参数
        if len(sys.argv) > 1 and sys.argv[1] == "--reload":
            run_with_reload()
        else:
            run()

