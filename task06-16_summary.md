# DCC Hub 项目上下文摘要

## Project Capsule & Architecture Map

**项目目标**：在 Maya 2022-2026 上构建最小可用 Hub，统一工具管理平台。

**架构层次**：
- Hub 层：Qt.py AppShell（MainWindow/CommandBus/EventBus/ToolRegistry/Settings/JobCenter）
- DCC Adapter 层：Facade 接口抽象（Maya/Max 后端实现）
- Services 层：AIGC/HDA 服务客户端（当前为占位）
- Plugins 层：工具插件（poly/anim/aigc/integrations）

**当前进度**（本次完成任务 06-16）：
- ✓ CommandBus（同步调用）
- ✓ EventBus（发布/订阅）
- ✓ Settings（用户级 JSON 读写）
- ✓ StateStore（会话态字典）
- ✓ 撤销块上下文（Maya）
- ✓ MayaFacade 基本方法实现
- ✓ BaseToolPlugin 与 ToolContext
- ✓ ToolRegistry（manifest 扫描与实例化）
- ✓ 首个插件：poly.smooth_normals
- ✓ MainWindow 动态装载插件面板
- ✓ Smooth Normals 实际逻辑（修复中）

**下一步任务**：任务 17 - 将插件执行注册为 CommandBus 命令

## Constraints & Invariants

1. **Maya 版本兼容**：必须支持 Maya 2022-2026
2. **Qt 导入策略**：优先 vendor 中的 Qt.py，回退到 DCC 的 PySide2/PySide6，最后使用 stub
3. **路径注入顺序**：vendor/thirdparty_libs → DCC_Hub → maya_tools_hub
4. **编码要求**：所有文件使用 UTF-8，exec() 必须指定 encoding='utf-8'
5. **模块导入路径**：通过 exec() 执行后使用完整路径 `maya_tools_hub.xxx`
6. **热重载范围**：只清除 hub 包模块，保留外部依赖（Qt/maya）
7. **任务执行原则**：一次只完成一个任务，完成后等待测试
8. **代码风格**：最小代码完成当前任务，不进行大规模改动

## Decisions Log

1. **窗口引用保持机制** → 避免窗口被垃圾回收导致一闪而过
2. **hub_launcher.py 检查 __file__ 存在性** → 防止 exec() 执行时自动运行导致重复窗口
3. **获取 Maya 主窗口作为 parent** → 防止窗口在选择物体时最小化
4. **使用 raise_() 和 activateWindow()** → 确保窗口显示在前台
5. **按钮引用保存为实例变量** → 防止信号连接被垃圾回收
6. **使用 lambda 连接按钮信号** → 确保正确的 self 绑定
7. **polySoftEdge 先选择边再应用** → 确保命令正确执行
8. **移除初始化时的测试代码** → 避免在启动时执行不必要的操作
9. **Settings 支持点号分隔键** → 便于组织配置层次结构
10. **ToolRegistry 自动扫描 plugins/*/*/manifest.json** → 简化插件发现流程
11. **MainWindow 接收 registry 和 context** → 支持动态加载插件
12. **插件 UI 创建时保存控件引用** → 确保信号连接有效

## Open TODO (Next 3)

1. **任务 17：将插件执行注册为 CommandBus 命令**
   - 在 `app.run()` 注册 `tool.execute`，内部 `registry.instantiate(key, ctx)` → `tool.execute(**kwargs)`
   - 插件 UI 的按钮改为分发命令
   - 完成标准：点击按钮后 `execute()` 被间接调用

2. **任务 18：事件总线：工具完成广播**
   - 工具执行后通过 `EventBus` 广播完成事件
   - 在 `execute()` 尾部 `event_bus.publish("tool/done", payload)`
   - 完成标准：执行后控制台面板出现 `tool/done` 记录

3. **修复任务 16 遗留问题**：
   - Smooth Normals 效果不正确，参数意义不明
   - 需要重新研究 polySoftEdge 的正确用法和参数含义
   - 触发方式和撤销逻辑已正确，无需修改

## Glossary

- **CommandBus**：命令总线，同步调用模式，统一触发工具执行
- **EventBus**：事件总线，发布/订阅模式，解耦组件通信
- **ToolContext**：工具上下文，包含 dcc/settings/state/cmd_bus/evt_bus/job_center/services
- **BaseToolPlugin**：插件抽象基类，包含 create_ui() 和 execute() 抽象方法
- **ToolRegistry**：插件注册中心，扫描 manifest.json 并动态实例化插件
- **manifest.json**：插件清单文件，包含 key/label/category/entry/ui 配置
- **polySoftEdge**：Maya 命令，用于软化多边形网格的法线
- **Maya 主窗口 parent**：将 Hub 窗口设置为 Maya 主窗口的子窗口，防止最小化
- **窗口引用保持**：使用模块级变量保存窗口实例，避免被垃圾回收

## Context Attachments

**关键文件路径**：
- `DCC_Hub/architecture.md` - 架构设计文档
- `DCC_Hub/tasks.md` - 任务清单（30 个任务，当前完成 16）
- `DCC_Hub/task17-18_summary.md` - 任务 17-18 完成摘要
- `DCC_Hub/maya_test_code.md` - 当前任务测试代码
- `DCC_Hub/maya_tools_hub/hub/app.py` - AppShell 主入口（包含 get_maya_main_window）
- `DCC_Hub/maya_tools_hub/hub/core/command_bus.py` - 命令总线
- `DCC_Hub/maya_tools_hub/hub/core/event_bus.py` - 事件总线
- `DCC_Hub/maya_tools_hub/hub/core/settings.py` - 用户设置管理
- `DCC_Hub/maya_tools_hub/hub/core/state_store.py` - 会话态容器
- `DCC_Hub/maya_tools_hub/hub/core/undo.py` - 撤销块上下文管理器
- `DCC_Hub/maya_tools_hub/hub/core/plugins.py` - 插件基类与上下文
- `DCC_Hub/maya_tools_hub/hub/core/registry.py` - 插件注册中心
- `DCC_Hub/maya_tools_hub/hub/dcc/maya_backend.py` - Maya 后端实现
- `DCC_Hub/maya_tools_hub/hub/ui/main_window.py` - 主窗口（支持动态加载插件）
- `DCC_Hub/maya_tools_hub/hub/plugins/poly/smooth_normals/plugin.py` - Smooth Normals 插件
- `DCC_Hub/maya_tools_hub/hub/plugins/poly/smooth_normals/manifest.json` - 插件清单

**重要提示**：在新会话中引用文件时使用 `@文件名` 格式。

