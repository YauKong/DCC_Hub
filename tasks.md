# Maya/3ds Max 工具 Hub —— MVP 分步计划（Markdown）

> 目标：在 **Maya 2022–2026** 上跑通最小可用 Hub（1 个主窗口、1 个插件、统一命令/事件总线、撤销块、设置与状态、JobCenter 雏形、AIGC/HDA 以空实现占位）。再留出 3ds Max 适配位点，但不纳入本次 MVP 验收。

**执行方式**：一次仅执行一个任务。每个任务均满足：小且可测、明确开始/结束、专注一个点、按顺序排列。
**验证方式**：所有任务都给出「验收标准」与「可重复测试步骤」。

---

## 阶段 0：仓库与运行基线

### 01. 初始化仓库与基础结构

* **目标**：创建最小目录树与入口脚本占位。
* **开始条件**：空仓库。
* **结束条件**：目录按文档创建，`hub_launcher.py` 能被 Python 解释器导入（不执行 GUI）。
* **步骤**：

  1. 创建 `maya_tools_hub/` 与文档中列出的一级目录。
  2. 写空文件（`__init__.py`、`README.md`、`.gitignore`、`pyproject.toml` 占位）。
  3. `hub_launcher.py` 内仅 `if __name__ == "__main__": print("ok")`。
* **验收标准**：`python hub_launcher.py` 输出 `ok`。
* **产物**：初始仓库骨架。

### 02. 引入 Qt.py 依赖与最小 AppShell 占位

* **目标**：引入 Qt.py 并准备 `hub/app.py` 的 `run()` 空函数。
* **开始条件**：任务 01 完成。
* **结束条件**：`from Qt import QtWidgets` 可导入；`run()` 存在且返回 `0`。
* **步骤**：

  1. 安装 Qt.py 到 `hub/vendor/thirdparty_libs/`（`pip install Qt.py --target hub/vendor/thirdparty_libs`）。
  2. 在 `hub_launcher.py` 中优先添加 vendor 路径到 `sys.path`。
  3. 创建 `hub/core/qt_import.py` 统一导入工具（优先使用 vendor 的 Qt.py，回退到 DCC 的 Qt 或 stub）。
  4. 在 `hub/app.py` 定义 `run()`，内部仅 `return 0`。
  5. 在 `hub_launcher.py` 中调用 `from hub.app import run; print(run())`。
* **验收标准**：`python hub_launcher.py` 输出 `0`；vendor 中的 Qt.py 优先被使用。
* **产物**：可导入的 AppShell 占位；Qt 导入工具；vendor 依赖管理。

---

## 阶段 1：DCC 适配最小闭环（Maya）

### 03. 创建 DCC Facade 接口与 Maya 实现空类

* **目标**：定义 `hub/dcc/api.py` 接口与 `hub/dcc/maya_backend.py` 空实现。
* **开始条件**：任务 02 完成。
* **结束条件**：`MayaFacade` 可被实例化但无实际方法逻辑。
* **步骤**：

  1. 在 `api.py` 定义 `DCCFacade` 抽象方法：`get_selection()`, `undo_chunk(label)`, `show_message(text, level)`.
  2. 在 `maya_backend.py` 定义 `MayaFacade(DCCFacade)`，方法体 `raise NotImplementedError`。
* **验收标准**：`from hub.dcc.maya_backend import MayaFacade; MayaFacade()` 不报导入错误。
* **产物**：接口与空实现。

### 04. 检测 Maya 环境与 Facade 选择器

* **目标**：在 `hub/app.py` 中实现 `detect_dcc()`，仅返回 `MayaFacade()`
* **开始条件**：任务 03 完成。
* **结束条件**：`detect_dcc()` 返回 `MayaFacade` 实例（即使未在 Maya 中运行）。
* **步骤**：

  1. `detect_dcc()` 直接 `return MayaFacade()  # stub`
  2. `run()` 调用 `detect_dcc()` 并 `print(dcc.name if hasattr(dcc, "name") else "Maya")`。
* **验收标准**：`python hub_launcher.py` 打印出 `Maya` 或设定的占位字符串。
* **产物**：DCC 选择器雏形。

### 05. 在 Maya 环境内启动最小窗口（本地测试）

* **目标**：在 Maya Script Editor 运行 `hub_launcher.py` 启动一个空 `QWidget`。
* **开始条件**：任务 04 完成。
* **结束条件**：Maya 内可弹出空白窗口。
* **步骤**：

  1. 在 `hub/ui/main_window.py` 定义 `MainWindow(QtWidgets.QWidget)`，`setWindowTitle("Hub MVP")`。
  2. 在 `app.run()`：`app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])` → 创建 `MainWindow` 并 `show()` → `app.exec_()`。
  3. 在 `hub_launcher.py` 中添加热重载功能：`reload_hub()` 清除 `sys.modules` 中的 hub 模块缓存，`run_with_reload()` 支持 `--reload` 参数。
* **验收标准**：Maya 中导入并调用 `hub.app.run()`，出现名为 “Hub MVP” 的窗体。修改代码后使用 `python hub_launcher.py --reload` 或调用 `reload_hub()` 可看到最新更改。
* **产物**：Maya 内部 GUI 出窗；热重载支持（开发时无需重启 Maya）。

---

## 阶段 2：核心总线与设置/状态

### 06. 建立 CommandBus（同步调用）

* **目标**：`hub/core/command_bus.py` 可注册/分发函数。
* **开始条件**：任务 05 完成。
* **结束条件**：注册一个 `echo` 命令并成功调用。
* **步骤**：

  1. 实现 `register(name, func)`、`dispatch(name, **kwargs) -> any`。
  2. 在 `app.run()` 内部注册 `echo` → `dispatch("echo", msg="hi")`。
* **验收标准**：控制台打印/返回 `hi`。
* **产物**：同步命令总线。

### 07. 建立 EventBus（发布/订阅）

* **目标**：`hub/core/event_bus.py` 可订阅主题并收到发布消息。
* **开始条件**：任务 06 完成。
* **结束条件**：订阅 `"mvp/test"` 并接收一次消息。
* **步骤**：

  1. 实现 `subscribe(topic, callback)`、`publish(topic, payload)`。
  2. 在 `run()` 里订阅并立刻 `publish("mvp/test", {"ok":1})`。
* **验收标准**：回调被调用（打印 `ok:1`）。
* **产物**：事件总线基础。

### 08. Settings（用户级 JSON）读写

* **目标**：实现 `hub/core/settings.py`，提供 `get/set/save/load`。
* **开始条件**：任务 07 完成。
* **结束条件**：可在用户 Home 下生成 `user_settings.json`。
* **步骤**：

  1. `~/.studio_name/maya_tools_hub/user_settings.json` 作为默认路径。
  2. `set("ui.theme","dark")` → `save()` → `load()` 后可读回。
* **验收标准**：文件生成且 JSON 包含 `ui.theme: "dark"`。
* **产物**：持久化配置。

### 09. StateStore（会话态）字典

* **目标**：实现 `hub/core/state_store.py` 的内存状态容器。
* **开始条件**：任务 08 完成。
* **结束条件**：`state["last_panel"]="home"` 后在同一会话可取回。
* **步骤**：

  1. `class StateStore(dict): pass` 即可。
* **验收标准**：运行期存取成功（无持久化）。
* **产物**：会话态容器。

---

## 阶段 3：撤销块与 Maya 适配基本方法

### 10. 撤销块上下文（Maya）

* **目标**：实现 `hub/core/undo.py` 的 `maya_undo_chunk(label)`。
* **开始条件**：任务 09 完成。
* **结束条件**：上下文可在无 Maya 时安全导入（但在 Maya 外不执行）。
* **步骤**：

  1. 用 `try/except ImportError` 包装 `maya.cmds` 引用。
  2. 上下文管理器打开/关闭 `cmds.undoInfo`。
* **验收标准**：在非 Maya 解释器可导入模块；在 Maya 内部执行不报错。
* **产物**：撤销块工具。

### 11. MayaFacade：实现 `name/get_selection/undo_chunk/show_message`

* **目标**：让 Facade 具备最小可用能力。
* **开始条件**：任务 10 完成。
* **结束条件**：在 Maya 内调用这些方法可工作。
* **步骤**：

  1. `name = "Maya"`。
  2. `get_selection()`：返回 `cmds.ls(sl=True, l=True) or []`。
  3. `undo_chunk()`：返回 `maya_undo_chunk(label)`。
  4. `show_message()`：`inViewMessage` 简单弹窗。
* **验收标准**：在 Maya 选中物体，`get_selection()` 返回正确；`show_message("hello")` 显示消息。
* **产物**：可用的最小 Maya 后端。

---

## 阶段 4：插件注册与首个工具（Poly：Smooth Normals）

### 12. BaseToolPlugin 与 ToolContext

* **目标**：实现 `hub/core/plugins.py` 的基类与上下文。
* **开始条件**：任务 11 完成。
* **结束条件**：可被具体插件继承。
* **步骤**：

  1. 定义 `ToolContext(dcc, settings, state, cmd_bus, evt_bus, job_center, services)`。
  2. `BaseToolPlugin` 含 `create_ui(parent)`、`execute(**kwargs)` 抽象。
* **验收标准**：可实例化子类（未执行）。
* **产物**：插件基类。

### 13. ToolRegistry（manifest 扫描与实例化）

* **目标**：实现 `hub/core/registry.py` 的发现/加载。
* **开始条件**：任务 12 完成。
* **结束条件**：能扫描 `plugins/*/*/manifest.json` 并实例化工具类。
* **步骤**：

  1. 解析 `entry` 为 `module:Class`，使用 `importlib` 动态加载。
  2. `instantiate(key, ctx)` 返回 `(tool_instance, manifest)`。
* **验收标准**：日志打印已发现的工具键。
* **产物**：插件注册中心。

### 14. 创建首个插件：`poly.smooth_normals`

* **目标**：在 `hub/plugins/poly/smooth_normals/` 构建最小插件与 manifest。
* **开始条件**：任务 13 完成。
* **结束条件**：插件 `create_ui()` 返回一个按钮；`execute()` 打印接收到的角度参数。
* **步骤**：

  1. `manifest.json` 写入 `key/label/category/entry/ui.panel=true`。
  2. `plugin.py`：`SmoothNormalsTool(BaseToolPlugin)`。
  3. `create_ui` 返回含 `QDoubleSpinBox + QPushButton` 的小部件。
* **验收标准**：主面板可显示插件 UI；点击按钮调用 `execute(angle=xx)`。
* **产物**：首个面板插件（空实现）。

### 15. 在 MainWindow 动态装载插件面板（Poly 标签）

* **目标**：Panel 能从 Registry 动态装入 `ui.panel=true` 的插件。
* **开始条件**：任务 14 完成。
* **结束条件**：主 UI 的 “Poly” 页签显示 `Smooth Normals` 小部件。
* **步骤**：

  1. `MainWindow` 创建 TabWidget：Home/Poly。
  2. Poly 页签遍历 Registry，符合 `category="poly"` 的插件，逐一 `create_ui()` 并添加。
* **验收标准**：Maya 内主窗 Poly 页签可见插件控件。
* **产物**：动态面板装配。

### 16. 完成 Smooth Normals 的实际逻辑

* **目标**：`execute(angle, keep_hard)` 调用 Maya 命令完成软硬边处理。
* **开始条件**：任务 15 完成。
* **结束条件**：选中网格后点击按钮，法线被软化（或保持硬边）。
* **步骤**：

  1. 在 `execute()`：拿 `dcc.get_selection()`。
  2. 用 `with dcc.undo_chunk("SmoothNormals"):` 包裹 `cmds.polySoftEdge()`
* **验收标准**：在 Maya 观察到法线变化；撤销可恢复。
* **产物**：可工作的首个建模工具。

---

## 阶段 5：命令/事件整合与 JobCenter 雏形

### 17. 将插件执行注册为 CommandBus 命令

* **目标**：`CommandBus` 可统一触发工具执行。
* **开始条件**：任务 16 完成。
* **结束条件**：UI 点击 → 通过 `dispatch("tool.execute", key, kwargs)` 触发。
* **步骤**：

  1. 在 `app.run()` 注册 `tool.execute`，内部 `registry.instantiate(key, ctx)` → `tool.execute(**kwargs)`。
  2. 插件 UI 的按钮改为分发命令。
* **验收标准**：点击按钮后 `execute()` 被间接调用。
* **产物**：命令化工具触发。

### 18. 事件总线：工具完成广播

* **目标**：工具执行后通过 `EventBus` 广播完成事件。
* **开始条件**：任务 17 完成。
* **结束条件**：订阅 `tool/done` 可收到 `{"key":..., "result":...}`。
* **步骤**：

  1. 在 `execute()` 尾部 `event_bus.publish("tool/done", payload)`。
  2. UI 控制台面板（简单 QTextEdit）打印收到的事件。
* **验收标准**：执行后控制台面板出现 `tool/done` 记录。
* **产物**：事件回流。

### 19. JobCenter 空实现（线程与信号）

* **目标**：实现 `hub/core/job_center.py` 的最小 `run_in_thread(fn)`。
* **开始条件**：任务 18 完成。
* **结束条件**：可提交一个 2 秒延迟的假任务，并通过信号回调完成。
* **步骤**：

  1. `_Worker` 在 `QThread` 运行 `time.sleep(2)` 后返回 `{"ok":1}`。
  2. `JobCenter.finished` 发出后，UI 控制台打印。
* **验收标准**：点击按钮提交任务 → 2 秒后打印完成。
* **产物**：后台任务雏形。

---

## 阶段 6：设置与状态打通到插件

### 20. 插件读取默认参数（Settings）

* **目标**：`SmoothNormals` 加载默认角度自 `settings`。
* **开始条件**：任务 19 完成。
* **结束条件**：若 `settings["poly.smooth_normals.angle"]=45`，UI 初始为 45。
* **步骤**：

  1. 插件 `__init__` 读取 `ctx.settings.get("poly.smooth_normals.angle", 60)`.
  2. `create_ui()` 将值设置到 `QDoubleSpinBox`。
* **验收标准**：更改配置后重启 UI，角度初值生效。
* **产物**：设置与 UI 绑定。

### 21. 插件写回上次参数（StateStore）

* **目标**：执行后将参数写入会话态，供下次复用（不持久化）。
* **开始条件**：任务 20 完成。
* **结束条件**：同一会话内再次打开 UI，读取 `state` 值作为初值。
* **步骤**：

  1. `execute()` 结束：`ctx.state["poly.smooth_normals.last_angle"]=angle`。
  2. `create_ui()` 优先读 `state` 值。
* **验收标准**：同会话第二次打开 UI，显示为上次角度。
* **产物**：会话态记忆。

---

## 阶段 7：日志与错误处理

### 22. 统一日志：简单 Logger

* **目标**：在 `hub/core/logging.py` 提供 `get_logger(__name__)`。
* **开始条件**：任务 21 完成。
* **结束条件**：日志打印到控制台面板（或 stdout）。
* **步骤**：

  1. 标准 `logging` 配置。
  2. 在关键路径（加载、执行、异常）写日志。
* **验收标准**：运行时可读有序日志。
* **产物**：基础日志。

### 23. 异常捕获与用户提示

* **目标**：对插件 `execute()` 包装 try/except，出错弹 `show_message`。
* **开始条件**：任务 22 完成。
* **结束条件**：模拟抛错时 UI 出提示，日志有堆栈，事件 `tool/failed` 发布。
* **步骤**：

  1. 装饰器或统一包装点。
  2. `evt_bus.publish("tool/failed", {"key":..., "error":...})`
* **验收标准**：注入异常 → 用户消息与日志/事件均可见。
* **产物**：健壮性基础。

---

## 阶段 8：AIGC/HDA 服务占位

### 24. Services 容器与空客户端注入

* **目标**：在 `app.run()` 的 `ctx.services = {"aigc": AigcClientStub(), "hda": HdaBridgeStub()}`。
* **开始条件**：任务 23 完成。
* **结束条件**：两者类存在但仅打印调用参数。
* **步骤**：

  1. `services/aigc_client.py`：`submit(inputs)->job_id`、`poll(job_id)->status`。
  2. `services/hda_bridge.py`：`run_hda(hda_path, parms)->outputs`。
* **验收标准**：调用这些函数时日志打印调用参数。
* **产物**：可替换的服务接口。

### 25. JobCenter + AIGC Stub 流程打通

* **目标**：新增 “假 AIGC 任务” 按钮，提交流程 → 2s 后回调完成。
* **开始条件**：任务 24 完成。
* **结束条件**：事件 `aigc/done` 发布并出现在控制台。
* **步骤**：

  1. 在 Home 页添加按钮 `Submit Fake AIGC Job`。
  2. 点击后 `job_center.run_in_thread(fake_submit_and_poll)`.
* **验收标准**：按钮 → 等待 → 控制台出现 `aigc/done {job_id:...}`。
* **产物**：端到端占位流程。

---

## 阶段 9：UI 打磨与装配测试

### 26. 面板：Home/Poly/Console 三页

* **目标**：统一主 Tab：`Home`、`Poly`、`Console`。
* **开始条件**：任务 25 完成。
* **结束条件**：三页存在且可切换。
* **步骤**：

  1. `panel_home.py`：显示环境信息、AIGC 按钮。
  2. `panel_poly.py`：动态添加 `SmoothNormals`。
  3. `widgets/console.py`：订阅 EventBus 打印事件。
* **验收标准**：Maya 内视觉与功能如上。
* **产物**：可操作的 MVP UI。

### 27. 轻量主题（QSS）与图标占位

* **目标**：加入简单 QSS 与 1 个图标占位（本地路径）。
* **开始条件**：任务 26 完成。
* **结束条件**：加载 QSS 不报错，图标出现在按钮上。
* **步骤**：

  1. `ui/style/main.qss`。
  2. `resources/icons/placeholder.svg`。
  3. 主窗体 `setStyleSheet(...)`。
* **验收标准**：界面明显变化；无路径错误。
* **产物**：基础风格。

---

## 阶段 10：可部署与最小打包

### 28. 启动脚本：Maya 按钮/菜单

* **目标**：在 `tools/install_scripts/` 增加 Maya 启动脚本（创建 Shelf 按钮）。
* **开始条件**：任务 27 完成。
* **结束条件**：点击 Shelf 按钮即可打开 Hub。
* **步骤**：

  1. MEL 或 Python：添加 shelf 按钮绑定 `hub_launcher.py`。
  2. 文档：手动安装步骤（复制脚本到 `~/Documents/maya/<ver>/scripts`）。
* **验收标准**：通过按钮打开 Hub。
* **产物**：入口集成。

### 29. 依赖路径注入与 vendor 测试

* **目标**：在 `hub_launcher.py` 注入 `vendor/thirdparty_libs` 到 `sys.path`。
* **开始条件**：任务 28 完成。
* **结束条件**：断网/无外网依赖仍可启动。
* **步骤**：

  1. 将 Qt.py（若需）与必需小库复制到 `vendor/thirdparty_libs/`。
  2. 启动注入 `sys.path.insert(0, vendor_path)`。
* **验收标准**：在隔离环境可启动 Hub。
* **产物**：离线可运行。

### 30. 最小集成测试脚本

* **目标**：在 `tests/integration/` 写 3 个脚本：启动、执行 SmoothNormals、提交 Fake AIGC。
* **开始条件**：任务 29 完成。
* **结束条件**：脚本在 Maya 内逐步打印通过。
* **步骤**：

  1. `test_boot.py`：导入与 `run()`。
  2. `test_smooth_normals.py`：选一个立方体 → 执行命令 → 校验返回值。
  3. `test_fake_aigc.py`：提交任务 → 等待信号 → 打印 done。
* **验收标准**：三脚本在 Log 中统一打印 `PASS`。
* **产物**：端到端验证最小集。

---

## 附：每阶段的可选回归清单（执行后 2 分钟内可完成）

* **阶段 1 回归**：能在 Maya 打开空窗并关闭；无崩溃。
* **阶段 2 回归**：`CommandBus/EventBus` 的 demo 能正常打印。
* **阶段 3 回归**：撤销块可用；`show_message` 可提示。
* **阶段 4 回归**：`SmoothNormals` 能改变法线；撤销恢复。
* **阶段 5 回归**：命令触发与事件广播同步工作。
* **阶段 6 回归**：Settings 初值与 State 会话记忆生效。
* **阶段 7 回归**：异常能提示且日志有栈。
* **阶段 8 回归**：假 AIGC 流程 2 秒内完成并广播。
* **阶段 9 回归**：三页 UI 可切换，Console 有事件流。
* **阶段 10 回归**：Shelf 启动、离线依赖、三条集成测试 `PASS`。

---

## MVP 完成定义（Definition of Done）

* 在 **Maya 2022–2026** 中：

  * 点击 Shelf 按钮可打开 Hub 主窗口。
  * **Poly** 页有 **Smooth Normals** 插件，能在选中网格上执行并可撤销。
  * **Home** 页能提交一次 **Fake AIGC** 任务，2 秒后完成并在 **Console** 页显示事件日志。
  * **Settings** 可持久化 UI 默认值，**State** 可记住会话内上次参数。
  * 出错时用户得到提示且日志记录堆栈。
* 目录与代码结构与设计文档一致，测试脚本通过。
