# Maya/3ds Max Tools Hub

DCC 工具集线器 - 统一的工具管理平台。

## 快速开始

### 在 Maya 中运行

在 Maya Script Editor 中执行以下代码（将路径替换为你的实际路径）：

```python
# 注意：必须指定 encoding='utf-8' 以避免 Windows 编码问题
exec(open(r"E:\workspace\cursor_playground\DCC_Hub\maya_tools_hub\hub_launcher.py", encoding='utf-8').read())
```

## 开发调试

### 热重载（开发时使用）

修改代码后无需重启 Maya，使用热重载功能即可看到更改。

#### 使用方法

**方法 1：使用 run_with_reload()（推荐）**

```python
import sys
sys.path.insert(0, r"E:\workspace\cursor_playground\DCC_Hub")

# 导入 launcher（必须指定 encoding='utf-8'）
exec(open(r"E:\workspace\cursor_playground\DCC_Hub\maya_tools_hub\hub_launcher.py", encoding='utf-8').read())

# 使用热重载运行（使用完整模块路径）
from maya_tools_hub.hub_launcher import run_with_reload
run_with_reload()
```

**方法 2：手动调用 reload_hub()**

```python
import sys
sys.path.insert(0, r"E:\workspace\cursor_playground\DCC_Hub")

# 导入 launcher（必须指定 encoding='utf-8'）
exec(open(r"E:\workspace\cursor_playground\DCC_Hub\maya_tools_hub\hub_launcher.py", encoding='utf-8').read())

# 清除缓存（使用完整模块路径）
from maya_tools_hub.hub_launcher import reload_hub
reload_hub()

# 重新导入并运行（使用完整模块路径）
from maya_tools_hub.hub.app import run
run()
```

**方法 3：创建便捷函数（推荐开发时使用）**

在 Maya Script Editor 中创建以下函数，每次修改代码后调用：

```python
import sys
import os

# 设置项目路径
project_path = r"E:\workspace\cursor_playground\DCC_Hub"
if project_path not in sys.path:
    sys.path.insert(0, project_path)

def reload_and_run_hub():
    """热重载并运行 Hub - 开发时使用"""
    # 导入 launcher（首次需要，必须指定 encoding='utf-8'）
    if 'maya_tools_hub.hub_launcher' not in sys.modules:
        exec(open(os.path.join(project_path, "maya_tools_hub", "hub_launcher.py"), encoding='utf-8').read())
    
    # 使用热重载（使用完整模块路径）
    from maya_tools_hub.hub_launcher import run_with_reload
    run_with_reload()

# 使用
reload_and_run_hub()
```

#### 工作原理

`reload_hub()` 函数会：
1. 查找 `sys.modules` 中所有以 `hub.` 开头的模块
2. 删除这些模块的缓存
3. 下次导入时会重新加载最新代码

**注意：**
- 只清除 `hub` 包及其子模块，保留外部依赖（Qt、maya 等）
- 如果修改了外部依赖的代码，可能需要重启 Maya
- 某些深层修改（如类定义变更）可能需要重启窗口

## 常见问题

### 问题 1：ImportError: No module named 'hub'

**解决方案：**
- 确保项目路径正确添加到 `sys.path`
- 检查路径中是否包含 `maya_tools_hub` 目录（应该只到 `DCC_Hub`）

### 问题 2：Qt not available 警告

**解决方案：**
- 在 Maya 中不应该出现此警告
- 如果出现，检查 Maya 版本是否支持 PySide2/PySide6
- 确保在 Maya 的 Python 环境中运行，而不是系统 Python

### 问题 3：窗口不显示

**解决方案：**
- 检查 Maya 是否在运行
- 确保使用 Maya 的 Script Editor，而不是外部 Python 解释器
- 窗口可能被 Maya 主窗口遮挡，检查任务栏

### 问题 4：路径问题（Windows）

**解决方案：**
- 使用原始字符串（`r"..."`）避免反斜杠转义问题
- 或者使用正斜杠：`"E:/workspace/cursor_playground/DCC_Hub"`

### 问题 5：UnicodeDecodeError（Windows 编码问题）

**错误信息：**
```
UnicodeDecodeError: 'charmap' codec can't decode byte 0x8d in position 688
```

**原因：**
Windows 上 Maya 的 Python 默认使用 cp1252 编码，而代码文件使用 UTF-8 编码（包含中文注释）。

**解决方案：**
在使用 `exec(open(...).read())` 时，必须指定 `encoding='utf-8'`：

```python
# 错误的方式（会导致编码错误）
exec(open(r"path\to\file.py").read())

# 正确的方式
exec(open(r"path\to\file.py", encoding='utf-8').read())
```

## 调试技巧

### 检查路径是否正确

```python
import sys
import os

print("Current sys.path:")
for p in sys.path:
    print("  ", p)

# 检查项目路径
project_path = r"E:\workspace\cursor_playground\DCC_Hub"
print("\nProject path exists:", os.path.exists(project_path))
print("Hub module exists:", os.path.exists(os.path.join(project_path, "maya_tools_hub", "hub")))
```

### 检查 Qt 版本

```python
import sys
sys.path.insert(0, r"E:\workspace\cursor_playground\DCC_Hub")

try:
    from Qt import QtWidgets
    print("Using Qt.py")
    print("Qt binding:", QtWidgets.__name__)
except:
    try:
        from PySide2 import QtWidgets
        print("Using PySide2 directly")
    except:
        try:
            from PySide6 import QtWidgets
            print("Using PySide6 directly")
        except:
            print("No Qt binding found")
```

## 项目结构

- `hub/` - 核心代码
- `hub_launcher.py` - 启动入口（自动处理路径、热重载支持）
- `Qt/` - Qt 兼容层（在 Maya 中使用真实 Qt，否则使用 stub）
- `tools/` - 工具脚本（测试脚本等）

## 注意事项

- `hub_launcher.py` 会自动将 `DCC_Hub` 目录和 vendor 依赖添加到 Python 路径
- 在 Maya 中，会自动使用 Maya 自带的 PySide2/PySide6（通过 vendor 中的 Qt.py）
- 在非 Maya 环境中，使用 stub 实现进行测试
- vendor 目录中的依赖需要手动安装：`pip install Qt.py --target hub/vendor/thirdparty_libs`
