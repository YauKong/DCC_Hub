更新maya_test_code.md的方法如下
1. 确保有两大板块
    - 在maya中运行的测试代码
    - 验收部分
        -测试步骤
        -验收标准
2. 可以参考以下模板
3. 不应记录已完成的任务，这应该放在summary中进行


# Maya 测试代码

## 当前任务：任务 18 - 事件总线：工具完成广播

### 验收标准
- 工具执行后通过 EventBus 广播完成事件
- 订阅 `tool/done` 可收到 `{"key":..., "result":...}`
- 执行后控制台面板出现 `tool/done` 记录

### 测试代码

在 Maya Script Editor 中运行：

```python
import sys

sys.path.insert(0, r"E:\workspace\cursor_playground\DCC_Hub")

exec(open(r"E:\workspace\cursor_playground\DCC_Hub\maya_tools_hub\hub_launcher.py", encoding='utf-8').read())

from maya_tools_hub.hub_launcher import run_with_reload
run_with_reload()
```

**测试步骤**：
1. 在 Maya 中创建一个多边形网格（如 polyCube）
2. 选中该网格
3. 运行代码，打开 Hub 窗口
4. 切换到 "Poly" 标签页
5. 在 "Smooth Normals" 插件中：
   - 设置角度值（如 60°）
   - 点击 "Smooth Normals" 按钮
6. 验证：
   - 工具执行后，控制台面板（Console 标签页）应该显示 `tool/done` 事件记录
   - 事件应该包含工具 key 和执行结果信息
   - 如果没有选中物体，应该显示警告消息
**验收标准**：
- UI 点击 → 通过 `dispatch("tool.execute", key, kwargs)` 触发
- 点击按钮后 `execute()` 被间接调用
---
