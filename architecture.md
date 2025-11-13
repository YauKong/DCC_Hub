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
maya_tools_hub/
├─ hub_launcher.py                    # 入口：环境检测、DCC识别、注入/启动
├─ pyproject.toml / setup.cfg         # 本地/可选打包配置
├─ README.md
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
