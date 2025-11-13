# DCC Hub 项目上下文摘要

## Project Capsule & Architecture Map

**项目目标**：在 Maya 2022-2026 上构建最小可用 Hub，统一工具管理平台。

**架构层次**：
- Hub 层：Qt.py AppShell（MainWindow/CommandBus/EventBus/ToolRegistry/Settings/JobCenter）
- DCC Adapter 层：Facade 接口抽象（Maya/Max 后端实现）
- Services 层：AIGC/HDA 服务客户端（当前为占位）
- Plugins 层：工具插件（poly/anim/aigc/integrations）

**当前进度**（已完成任务 01-05）：
- ✓ 仓库结构与基础文件
- ✓ Qt.py 依赖管理（vendor/thirdparty_libs）
- ✓ DCC Facade 接口与 Maya 空实现
- ✓ DCC 检测与选择器
- ✓ Maya 内最小窗口启动 + 热重载支持

**下一步任务**：任务 06 - 建立 CommandBus（同步调用）

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

1. **使用 Qt.py 而非直接 PySide** → 跨 DCC 兼容性
2. **依赖安装到 vendor/thirdparty_libs** → 支持离线部署
3. **hub_launcher.py 自动路径注入** → 简化使用
4. **热重载通过 sys.modules 清除** → 无需 importlib.reload
5. **exec() 执行方式统一** → 开发阶段标准流程
6. **README 只保留开发调试内容** → 聚焦当前阶段
7. **DCC_Hub 作为项目根目录** → 便于模块导入
8. **MayaFacade 当前为 stub** → 后续任务实现具体方法
9. **vendor 目录 gitignore** → 依赖需手动安装
10. **统一使用完整模块路径** → 避免导入歧义
11. **hub_launcher.py 处理 exec() 场景** → 支持 __file__ 不存在的情况
12. **Qt 导入工具独立模块** → 统一管理导入逻辑
13. **热重载函数暴露在 hub_launcher** → 便于外部调用
14. **删除 MAYA_TEST.md** → 合并到 README 避免重复
15. **Windows 编码问题通过 encoding 参数解决** → 不修改文件编码

## Open TODO (Next 3)

1. **任务 06：建立 CommandBus（同步调用）**
   - 实现 `hub/core/command_bus.py` 的 `register(name, func)` 和 `dispatch(name, **kwargs)`
   - 在 `app.run()` 中注册 `echo` 命令并测试调用
   - 完成标准：控制台打印/返回 `hi`

2. **任务 07：建立 EventBus（发布/订阅）**
   - 实现 `hub/core/event_bus.py` 的 `subscribe(topic, callback)` 和 `publish(topic, payload)`
   - 在 `run()` 中订阅 `"mvp/test"` 并发布消息
   - 完成标准：回调被调用（打印 `ok:1`）

3. **任务 08：Settings（用户级 JSON）读写**
   - 实现 `hub/core/settings.py` 的 `get/set/save/load`
   - 默认路径 `~/.studio_name/maya_tools_hub/user_settings.json`
   - 完成标准：文件生成且 JSON 包含 `ui.theme: "dark"`

## Glossary

- **DCC**：Digital Content Creation，数字内容创作软件（Maya/3ds Max）
- **Facade**：外观模式，为复杂子系统提供统一简化接口
- **CommandBus**：命令总线，同步调用模式，统一触发工具执行
- **EventBus**：事件总线，发布/订阅模式，解耦组件通信
- **ToolRegistry**：工具注册中心，扫描 manifest.json 并实例化插件
- **JobCenter**：任务中心，处理 AIGC/长任务，使用 QThread 异步执行
- **vendor/thirdparty_libs**：项目依赖目录，支持离线部署
- **热重载**：开发时清除模块缓存，无需重启 Maya 即可看到代码更改
- **hub_launcher.py**：项目入口脚本，自动处理路径注入和热重载
- **qt_import.py**：Qt 统一导入工具，处理不同环境的 Qt 绑定

## Context Attachments

**关键文件路径**：
- `DCC_Hub/architecture.md` - 架构设计文档
- `DCC_Hub/tasks.md` - 任务清单（30 个任务，当前完成 05）
- `DCC_Hub/maya_tools_hub/hub_launcher.py` - 启动入口（路径注入+热重载）
- `DCC_Hub/maya_tools_hub/hub/app.py` - AppShell 主入口
- `DCC_Hub/maya_tools_hub/hub/core/qt_import.py` - Qt 导入工具
- `DCC_Hub/maya_tools_hub/hub/dcc/api.py` - DCC Facade 接口
- `DCC_Hub/maya_tools_hub/hub/dcc/maya_backend.py` - Maya 后端实现
- `DCC_Hub/maya_tools_hub/hub/ui/main_window.py` - 主窗口
- `DCC_Hub/maya_tools_hub/README.md` - 开发调试文档

**重要提示**：在新会话中引用文件时使用 `@文件名` 格式。

