# DCC Hub 项目上下文摘要

## Project Capsule & Architecture Map

**项目目标**：在 Maya 2022-2026 上构建最小可用 Hub，统一工具管理平台。

**架构层次**：
- Hub 层：Qt.py AppShell（MainWindow/CommandBus/EventBus/ToolRegistry/Settings/JobCenter）
- DCC Adapter 层：Facade 接口抽象（Maya/Max 后端实现）
- Services 层：AIGC/HDA 服务客户端（当前为占位）
- Plugins 层：工具插件（poly/anim/aigc/integrations）

**当前进度**（本次完成任务 17-18 + 窗口显示修复）：
- ✓ 窗口显示问题修复（Maya 主窗口作为 parent 时窗口正常显示）
- ✓ 插件执行注册为 CommandBus 命令（任务 17）
- ✓ 事件总线：工具完成广播（任务 18）

**下一步任务**：任务 19 - JobCenter 空实现（线程与信号）

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

1. **窗口标志始终设置为独立窗口** → 即使有 parent 也作为独立窗口显示，避免嵌入为子控件
2. **使用 WA_ShowOnScreen 属性** → 确保窗口显示在屏幕上
3. **添加详细调试输出** → 帮助诊断窗口创建和显示问题
4. **ToolRegistry 在实例化时存储插件 key** → 插件实例通过 _plugin_key 属性知道自己的 key，用于命令分发
5. **CommandBus 注册 tool.execute 命令** → 统一通过命令总线触发工具执行，解耦 UI 和插件逻辑
6. **插件按钮通过 CommandBus 分发命令** → 按钮点击时调用 `cmd_bus.dispatch("tool.execute", key=..., **kwargs)`
7. **工具执行完成后发布 tool/done 事件** → 在 tool_execute_handler 中执行完成后通过 EventBus 发布事件
8. **MainWindow 添加 Console 标签页** → 包含 QTextEdit 用于显示事件日志
9. **Console 面板订阅 tool/done 事件** → 自动显示工具执行完成的事件信息

## Open TODO (Next 3)

1. **任务 19：JobCenter 空实现（线程与信号）**
   - 实现 `hub/core/job_center.py` 的最小 `run_in_thread(fn)`
   - `_Worker` 在 `QThread` 运行 `time.sleep(2)` 后返回 `{"ok":1}`
   - `JobCenter.finished` 发出后，UI 控制台打印
   - 完成标准：点击按钮提交任务 → 2 秒后打印完成

2. **修复任务 16 遗留问题**（已记录，待后续修复）：
   - Smooth Normals 效果不正确，参数意义不明
   - 需要重新研究 polySoftEdge 的正确用法和参数含义
   - 触发方式和撤销逻辑已正确，无需修改

3. **任务 20：插件读取默认参数（Settings）**
   - `SmoothNormals` 加载默认角度自 `settings`
   - 若 `settings["poly.smooth_normals.angle"]=45`，UI 初始为 45
   - 完成标准：更改配置后重启 UI，角度初值生效

## Glossary

- **CommandBus**：命令总线，同步调用模式，统一触发工具执行
- **EventBus**：事件总线，发布/订阅模式，解耦组件通信
- **tool.execute**：CommandBus 命令，用于统一触发插件执行
- **tool/done**：EventBus 事件，工具执行完成后发布
- **_plugin_key**：插件实例属性，存储插件 key，用于命令分发
- **Console 面板**：MainWindow 中的事件日志显示面板
- **窗口标志**：Qt 窗口类型设置，确保窗口作为独立窗口显示

## Context Attachments

**关键文件路径**：
- `DCC_Hub/architecture.md` - 架构设计文档
- `DCC_Hub/tasks.md` - 任务清单（30 个任务，当前完成 18）
- `DCC_Hub/maya_test_code.md` - 当前任务测试代码
- `DCC_Hub/task06-16_summary.md` - 任务 06-16 完成摘要
- `DCC_Hub/maya_tools_hub/hub/app.py` - AppShell 主入口（包含 tool.execute 命令注册）
- `DCC_Hub/maya_tools_hub/hub/core/command_bus.py` - 命令总线
- `DCC_Hub/maya_tools_hub/hub/core/event_bus.py` - 事件总线
- `DCC_Hub/maya_tools_hub/hub/core/registry.py` - 插件注册中心（存储 _plugin_key）
- `DCC_Hub/maya_tools_hub/hub/ui/main_window.py` - 主窗口（包含 Console 标签页）
- `DCC_Hub/maya_tools_hub/hub/plugins/poly/smooth_normals/plugin.py` - Smooth Normals 插件（通过 CommandBus 分发）

**重要提示**：在新会话中引用文件时使用 `@文件名` 格式。

