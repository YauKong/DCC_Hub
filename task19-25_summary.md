# DCC Hub 项目上下文摘要

## Project Capsule & Architecture Map

**项目目标**：在 Maya 2022-2026 上构建最小可用 Hub，统一工具管理平台。

**架构层次**：
- Hub 层：Qt.py AppShell（MainWindow/CommandBus/EventBus/ToolRegistry/Settings/JobCenter）
- DCC Adapter 层：Facade 接口抽象（Maya/Max 后端实现）
- Services 层：AIGC/HDA 服务客户端（stub 占位）
- Plugins 层：工具插件（poly/anim/aigc/integrations）

**当前进度**（本次完成任务 19-25，跳过任务 20-21）：
- ✓ 任务 19：JobCenter 实现（QThread + Signal 异步任务）
- ✓ 任务 22：统一日志系统（get_logger + ConsoleHandler）
- ✓ 任务 23：异常捕获与用户提示（tool/failed 事件）
- ✓ 任务 24：Services 容器（AigcClientStub + HdaBridgeStub）
- ✓ 任务 25：JobCenter + AIGC Stub 流程（Home 页按钮 + aigc/done 事件）
- ✓ 线程安全修复（数据隔离 + 主线程回调）

**下一步任务**：任务 26 - 面板模块化（Home/Poly/Console 三页优化）

## Constraints & Invariants

1. **Maya 版本兼容**：必须支持 Maya 2022-2026
2. **线程安全原则**：Worker 线程不访问 Qt 控件和 Maya 场景，回调在主线程执行
3. **Qt 导入策略**：优先 vendor Qt.py，回退到 DCC PySide2/6
4. **日志级别使用**：INFO 重要操作，DEBUG 详细信息，WARNING 警告，ERROR 错误
5. **事件命名规范**：tool/done, tool/failed, job/done, job/failed, aigc/done
6. **编码要求**：所有文件 UTF-8，exec() 指定 encoding='utf-8'
7. **任务执行原则**：一次一任务，完成后测试验收
8. **代码风格**：最小代码完成任务，避免过度设计

## Decisions Log

1. **JobCenter 继承 QObject** → 使用 Qt 信号/槽机制实现线程安全通信
2. **Worker 在独立线程运行** → moveToThread() 确保工作函数在 QThread 执行
3. **数据提前提取传入闭包** → 避免在 Worker 线程访问 self 和 Qt 对象
4. **回调在主线程执行** → Qt 信号自动使用 QueuedConnection 跨线程
5. **Job ID 追踪机制** → _job_count 计数器标识每个任务
6. **Logger 输出双通道** → ConsoleHandler 同时写 stdout 和 Console 面板
7. **日志格式统一** → `[时间] [级别] [模块名] 消息`
8. **异常包装在 tool_execute_handler** → 统一捕获、日志、show_message、发布 tool/failed
9. **Services 容器依赖注入** → ctx.services 字典包含 aigc 和 hda 服务
10. **AIGC 任务流程** → submit → sleep(2) → poll → aigc/done 事件
11. **测试插件 Test Error** → 提供 3 种异常类型测试异常处理
12. **删除 TestPlugin stub** → app.py 清理测试代码减少冗余
13. **Console 订阅多事件** → tool/done, tool/failed, job/done, aigc/done
14. **线程清理使用 deleteLater** → 安全释放 Qt 对象资源
15. **跳过任务 20-21** → Settings/State 已在任务 8-9 实现，插件已集成

## Open TODO (Next 3)

1. **任务 26：面板模块化**
   - 创建 panel_home.py, panel_poly.py 独立面板类
   - MainWindow 动态加载面板而非硬编码
   - 完成标准：三页可切换，Console 有事件流

2. **修复任务 16 遗留问题**
   - Smooth Normals 效果不正确，polySoftEdge 参数需研究
   - 触发和撤销逻辑正确，仅需修正参数含义

3. **任务 27：轻量主题与图标**
   - ui/style/main.qss 样式表
   - resources/icons/ 图标占位
   - 完成标准：加载 QSS 不报错，图标显示在按钮

## Glossary

- **JobCenter**：异步任务管理器，使用 QThread 执行后台任务，信号回调通知完成
- **Worker**：QObject 工作对象，在 QThread 中执行用户函数，发出 finished/error 信号
- **线程安全**：Worker 函数不访问 Qt 控件/Maya 场景，回调在主线程通过信号机制
- **ConsoleHandler**：自定义 logging.Handler，同时输出到 stdout 和 Console 面板 QTextEdit
- **tool/failed**：工具执行失败事件，包含 key、error、error_type、kwargs
- **job/done**：后台任务完成事件，包含 job_id、result、status
- **aigc/done**：AIGC 任务完成事件，包含 job_id、status、inputs
- **AigcClientStub**：AIGC 服务占位实现，submit/poll/cancel 方法返回假数据
- **HdaBridgeStub**：Houdini HDA 桥接占位实现，run_hda/list_hdas 方法返回假数据
- **Test Error 插件**：测试异常处理的插件，触发 ValueError/RuntimeError/ZeroDivisionError

## Context Attachments

**关键文件路径**：
- `DCC_Hub/architecture.md` - 架构设计文档
- `DCC_Hub/tasks.md` - 任务清单（30 个，当前完成 25，跳过 20-21）
- `DCC_Hub/task17-18_summary.md` - 上一次摘要
- `DCC_Hub/maya_test_code.md` - 当前任务 25 测试代码
- `DCC_Hub/maya_tools_hub/hub/app.py` - AppShell（JobCenter 初始化，tool.execute 异常包装）
- `DCC_Hub/maya_tools_hub/hub/core/job_center.py` - JobCenter 线程安全实现
- `DCC_Hub/maya_tools_hub/hub/core/logging.py` - 统一日志系统
- `DCC_Hub/maya_tools_hub/hub/services/aigc_client.py` - AIGC Client Stub
- `DCC_Hub/maya_tools_hub/hub/services/hda_bridge.py` - HDA Bridge Stub
- `DCC_Hub/maya_tools_hub/hub/ui/main_window.py` - AIGC 按钮，事件订阅，线程安全回调
- `DCC_Hub/maya_tools_hub/hub/plugins/poly/test_error/` - 测试异常插件

**重要提示**：在新会话中引用文件时使用 `@文件名` 格式。

