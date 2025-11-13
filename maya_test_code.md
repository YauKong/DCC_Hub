# Maya 测试代码

## 当前任务：任务 11 - MayaFacade：实现 `name/get_selection/undo_chunk/show_message`

### 验收标准
- 在 Maya 选中物体，`get_selection()` 返回正确
- `show_message("hello")` 显示消息

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
1. 在 Maya 中选中一个或多个物体
2. 运行代码
3. 检查控制台输出：应该显示选中的物体路径
4. 检查 Maya 视图：应该显示 "hello" 消息弹窗

