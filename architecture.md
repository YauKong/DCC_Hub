总体架构图
+------------------------- Hub (Qt.py AppShell) --------------------------+
|  UI: MainWindow / Dock / Panels  |  CommandBus  |  EventBus             |
|  ToolRegistry  |  SettingsPanel  |  JobCenter   |  LogConsole           |
+--------------------+--------------------+------------------------------+
                     |                    |
                +----v----+          +---v----------------+
                |  DCC    |          |  Services          |
                | Adapter |          |  (AIGC, HDA, ...)  |
                +----+----+          +----+---------------+
                     |                    |
          +----------v-----------+   +----v----------------+
          | DCC Backends         |   | Network / Local IPC |
          | (Maya, Max, Common)  |   | HTTP/gRPC/QProcess  |
          +----------+-----------+   +---------------------+
                     |
           +---------v---------+
           | Tool Plugins      |
           | (Model/Anim/AIGC) |
           +-------------------+


文件与文件夹结构
DCC_Hub/                               # 项目根目录
├─ architecture.md                     # 架构设计文档
├─ tasks.md                            # 任务清单（30个任务）
├─ task01-05_summary.md                # 任务01-05完成摘要（示例）
├─ maya_test_code.md                   # Maya测试代码文档（当前任务测试代码）
├─ initiation_prompt.md                # 开发指引（AI助手工作流程）
├─ summary_prompt.md                   # 摘要生成指引（用于生成_summary.md）
│
maya_tools_hub/                        # Hub实现目录
├─ hub_launcher.py                     # 入口：环境检测、DCC识别、注入/启动、热重载支持
├─ pyproject.toml / setup.cfg          # 本地/可选打包配置
├─ README.md                           # 开发调试文档
├─ hub/
│  ├─ app.py                          # AppShell：MainWindow/Dock & 启停流程
│  ├─ ui/
│  │  ├─ main_window.py               # 主窗口/停靠窗口
│  │  ├─ panels/
│  │  │  ├─ panel_home.py             # 首页/概览
│  │  │  ├─ panel_poly.py             # 建模工具面板
│  │  │  ├─ panel_anim.py             # 技术动画面板
│  │  │  ├─ panel_aigc.py             # AIGC面板（任务/队列/进度）
│  │  │  └─ panel_integrations.py     # 外部接入（HDA等）
│  │  ├─ widgets/                     # 通用控件（日志、进度、搜索）
│  │  └─ style/                       # QSS/主题
│  ├─ core/
│  │  ├─ registry.py                  # ToolRegistry/插件发现/热加载
│  │  ├─ plugins.py                   # 插件基类/生命周期/manifest
│  │  ├─ command_bus.py               # 命令总线(CommandBus)
│  │  ├─ event_bus.py                 # 事件总线(EventBus)
│  │  ├─ job_center.py                # Job系统（AIGC/长任务/QThread）
│  │  ├─ settings.py                  # 配置读写（User/Project）
│  │  ├─ state_store.py               # 运行态存储（内存/会话缓存）
│  │  ├─ logging.py                   # 统一日志/埋点（可选）
│  │  └─ undo.py                      # DCC Undo 集成（chunk包装）
│  ├─ dcc/
│  │  ├─ api.py                       # DCC无关接口定义（Facade）
│  │  ├─ maya_backend.py              # Maya 实现（cmds/om2）
│  │  ├─ max_backend.py               # 3ds Max 实现（pymxs）
│  │  ├─ common.py                    # 通用几何/数学/mesh工具
│  │  └─ selection.py                 # 选择/命名空间/层级工具
│  ├─ services/
│  │  ├─ aigc_client.py               # AIGC服务HTTP/gRPC客户端
│  │  ├─ hda_bridge.py                # Houdini HDA 调用桥
│  │  └─ auth.py                      # 鉴权/Token/缓存
│  ├─ plugins/                        # 内置/第三方工具插件目录
│  │  ├─ poly/
│  │  │  ├─ smooth_normals/           # 平滑法线
│  │  │  │  ├─ __init__.py
│  │  │  │  ├─ plugin.py              # 具体工具实现
│  │  │  │  └─ manifest.json
│  │  │  ├─ corner_relax/             # 平滑转角顶点
│  │  │  ├─ deduplicate_elements/     # 重复边角面检测/清理
│  │  │  └─ guided_retopo/            # 引导减面/重拓扑
│  │  ├─ anim/
│  │  │  ├─ fkik_retarget/
│  │  │  ├─ muscle_skin_deform/
│  │  │  └─ weight_transfer/
│  │  ├─ aigc/
│  │  │  ├─ generate_model/
│  │  │  └─ upscale_texture/
│  │  └─ integrations/
│  │     └─ houdini_hda_runner/
│  └─ vendor/
│     └─ thirdparty_libs/             # 复制式依赖（无网部署）
├─ resources/
│  ├─ icons/
│  └─ presets/                        # 预设/规则模板
├─ tests/
│  ├─ unit/
│  └─ integration/
└─ tools/
   ├─ install_scripts/                # 安装/注入脚本（Maya shelf/Max菜单）
   └─ cli.py                          # 命令行工具（打包/发布/诊断）


项目文档说明
============

1. architecture.md（本文档）
   - 总体架构图和文件结构说明
   - 项目整体设计参考

2. tasks.md
   - 30个任务的详细清单
   - 每个任务包含：目标、开始条件、结束条件、步骤、验收标准
   - 按阶段组织，一次只完成一个任务

3. maya_test_code.md
   - 当前任务的测试代码
   - 包含验收标准和测试步骤
   - 每次完成任务后更新
   - 用法：在Maya Script Editor中运行文档中的代码进行测试

4. initiation_prompt.md
   - AI助手开发指引
   - 开发守则（CODING PROTOCOL）
   - 工作流程：阅读architecture.md和tasks.md → 按顺序完成任务 → 生成_summary.md

5. summary_prompt.md
   - 摘要生成模板
   - 用于生成任务完成摘要（taskXX-YY_summary.md）
   - 包含：项目胶囊、约束、决策日志、待办事项、术语表

6. taskXX-YY_summary.md
   - 已完成任务的上下文摘要
   - 用于新会话快速上手
   - 命名规则：task起始编号-结束编号_summary.md（如task01-05_summary.md）
