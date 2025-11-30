# Maya 测试代码

## 当前任务：任务 26 - 面板：Home/Poly/Console 三页

### 验收标准
- 统一主 Tab：`Home`、`Poly`、`Console`
- 三页存在且可切换
- Home 页显示环境信息、AIGC 按钮
- Poly 页动态添加 `SmoothNormals` 插件
- Console 页订阅 EventBus 打印事件

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

#### 1. 验证三个页签存在且可切换

1. 在 Maya 中运行代码，打开 Hub 窗口
2. 确认窗口正常显示
3. 验证主窗口有三个页签：
   - **Home** 页签
   - **Poly** 页签
   - **Console** 页签
4. 点击每个页签，验证可以正常切换
5. 确认切换时无错误日志

#### 2. 验证 Home 页功能

6. 切换到 **Home** 页签
7. 验证页面内容：
   - 显示 "Home" 标签
   - 显示 "Submit Fake AIGC Job" 按钮
8. 点击 "Submit Fake AIGC Job" 按钮
9. 验证：
   - 按钮点击后立即响应
   - Maya UI 保持响应（非阻塞）

#### 3. 验证 Poly 页功能

10. 切换到 **Poly** 页签
11. 验证页面内容：
    - 动态加载了 "Smooth Normals" 插件
    - 插件有标签显示 "Smooth Normals"
    - 插件有控件：角度输入框 + 按钮
    - 有分隔线分隔不同插件
12. 在 Maya 场景中创建一个立方体（polyCube）
13. 选中立方体
14. 在 Smooth Normals 插件中：
    - 设置角度值（如 60°）
    - 点击 "Smooth Normals" 按钮
15. 验证：
    - 工具正常执行
    - Console 页签显示 `tool/done` 事件

#### 4. 验证 Console 页功能

16. 切换到 **Console** 页签
17. 验证页面内容：
    - 有文本编辑框显示事件日志
    - 占位符文本："Event log will appear here..."
18. 切换回 **Home** 页签
19. 点击 "Submit Fake AIGC Job" 按钮
20. 切换到 **Console** 页签
21. 验证：
    - 立即显示提交确认消息
    - 2 秒后显示 `[aigc/done]` 事件
    - 显示完整的 AIGC 任务信息（job_id、inputs、status）
    - JSON 格式缩进美观
22. 切换回 **Poly** 页签
23. 执行 Smooth Normals 工具
24. 切换到 **Console** 页签
25. 验证：
    - 显示 `[tool/done]` 事件
    - 包含工具 key 和参数信息

#### 5. 验证模块化结构

26. 验证日志输出（Maya Script Editor）：
    - `[hub.ui.main_window] MainWindow initialized with modular panels`
    - `[hub.ui.panels.panel_home] Added AIGC test button to Home panel`
    - `[hub.ui.widgets.console] Console subscribed to tool/done, tool/failed, job/done, and aigc/done events`
    - `[hub.ui.panels.panel_poly] Loading plugin UI: poly.smooth_normals`
27. 确认无导入错误或模块找不到的错误

**验收标准**：

1. **三页存在且可切换**
   - Home、Poly、Console 三个页签都正常显示
   - 点击页签可以正常切换
   - 切换时无错误

2. **Home 页功能**
   - 显示 "Home" 标签
   - 显示 "Submit Fake AIGC Job" 按钮
   - 按钮点击正常，不阻塞 Maya UI
   - 使用模块化的 `HomePanel` 类

3. **Poly 页功能**
   - 动态加载 Poly 类别插件
   - 显示 "Smooth Normals" 插件 UI
   - 插件控件正常工作
   - 使用模块化的 `PolyPanel` 类

4. **Console 页功能**
   - 显示事件日志文本框
   - 订阅 `tool/done`, `tool/failed`, `job/done`, `aigc/done` 事件
   - 格式化显示事件信息
   - 自动滚动到最新消息
   - 使用模块化的 `ConsoleWidget` 类

5. **代码结构**
   - `main_window.py` 简洁（约100行），只负责组装面板
   - `panel_home.py` 独立模块，包含 AIGC 按钮逻辑
   - `panel_poly.py` 独立模块，包含插件加载逻辑
   - `console.py` 独立模块，包含事件订阅和显示逻辑
   - `panels/__init__.py` 和 `widgets/__init__.py` 存在

6. **事件流转**
   - AIGC 任务：Home 按钮 → JobCenter → aigc/done → Console 显示
   - 工具执行：Poly 插件 → tool.execute → tool/done → Console 显示
   - 所有事件都正确显示在 Console 页签

**成功标志**：
- ✅ 三页独立模块化（不再硬编码在 MainWindow）
- ✅ MainWindow 代码精简（从 357 行减少到约 100 行）
- ✅ 面板可复用（易于添加新页签）
- ✅ 职责分离清晰（UI 组装 vs 业务逻辑）
- ✅ 所有现有功能正常工作（AIGC、插件、事件）

**注意事项**：
- 这是 UI 重构任务，不改变功能逻辑
- 所有已有功能（任务 25）应保持正常工作
- Console widget 被 HomePanel 引用，需先创建
- 面板使用独立的 Python 模块，便于未来扩展
