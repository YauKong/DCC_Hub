# Maya 测试代码

## 当前任务：任务 25 - JobCenter + AIGC Stub 流程打通

### 验收标准
- 新增 "假 AIGC 任务" 按钮，提交流程 → 2s 后回调完成
- 事件 `aigc/done` 发布并出现在控制台
- 按钮 → 等待 → 控制台出现 `aigc/done {job_id:...}`

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

#### 1. 打开 Hub 窗口并验证按钮存在

1. 在 Maya 中运行代码，打开 Hub 窗口
2. 确认窗口正常显示
3. 切换到 "Home" 标签页
4. 验证看到 "Submit Fake AIGC Job" 按钮

#### 2. 提交 AIGC 任务

5. 点击 "Submit Fake AIGC Job" 按钮
6. 观察以下现象：
   - 按钮点击后立即响应
   - Console 标签页出现提示：`[INFO] AIGC job submitted, please wait...`
   - Maya UI 保持响应，可以自由操作：
     - 切换标签页
     - 移动视图
     - 选择物体

#### 3. 等待任务完成

7. 等待约 2 秒
8. 切换到 "Console" 标签页（如果不在的话）
9. 观察以下输出：
   - 看到 `[aigc/done]` 事件记录
   - 包含 job_id、inputs、status 等信息
   - 格式化的 JSON 输出

#### 4. 验证多次提交

10. 再次点击 "Submit Fake AIGC Job" 按钮
11. 验证可以多次提交任务
12. 每次任务都正确完成并显示结果

**验收标准**：

1. **UI 按钮**
   - Home 标签页显示 "Submit Fake AIGC Job" 按钮
   - 按钮样式正常，可点击

2. **任务提交**
   - 点击按钮后立即返回（非阻塞）
   - Console 显示提交确认消息
   - Maya UI 完全可用，不会冻结

3. **后台执行**
   - 任务在后台线程执行
   - AIGC Client 的 submit() 和 poll() 方法被调用
   - 日志显示完整的执行流程

4. **事件发布**
   - 2 秒后 `job/done` 事件发布
   - 检测到 AIGC 任务，自动发布 `aigc/done` 事件
   - Console 显示格式化的 AIGC 完成信息

5. **Console 显示**
   - 显示 `[aigc/done]` 标题
   - 显示 job_id
   - 显示 inputs（prompt、style、resolution）
   - 显示 status（state、progress、result）
   - JSON 格式缩进美观

**测试日志示例**：

```
[17:00:00] [INFO    ] [hub.ui.main_window] AIGC job submission requested
[17:00:00] [INFO    ] [hub.core.job_center] Submitting job to background thread: aigc_job
[17:00:00] [DEBUG   ] [hub.core.job_center] Starting worker thread
[INFO] AIGC job submitted, please wait...

[17:00:00] [DEBUG   ] [hub.core.job_center] Worker thread starting: <function aigc_job>
[17:00:00] [INFO    ] [hub.ui.main_window] AIGC job started in background thread
[17:00:00] [INFO    ] [hub.services.aigc_client] AigcClientStub.submit() called with inputs: {'prompt': 'Generate a sci-fi spaceship model', 'style': 'realistic', 'resolution': '2048x2048'}
[17:00:00] [INFO    ] [hub.ui.main_window] AIGC job submitted: job_a1b2c3d4

(等待 2 秒，Maya UI 完全可用)

[17:00:02] [INFO    ] [hub.services.aigc_client] AigcClientStub.poll() called with job_id: job_a1b2c3d4
[17:00:02] [INFO    ] [hub.ui.main_window] AIGC job completed: job_a1b2c3d4
[17:00:02] [DEBUG   ] [hub.core.job_center] Worker thread completed successfully
[17:00:02] [INFO    ] [hub.core.job_center] Job completed successfully, result: {'job_id': 'job_a1b2c3d4', ...}
[17:00:02] [DEBUG   ] [hub.core.job_center] Published job/done event
[17:00:02] [DEBUG   ] [hub.ui.main_window] Received job/done event: {...}
[17:00:02] [INFO    ] [hub.ui.main_window] Detected AIGC job completion, publishing aigc/done event
[17:00:02] [INFO    ] [hub.ui.main_window] AIGC job completed: job_a1b2c3d4

[aigc/done] AIGC Job Completed
  job_id: job_a1b2c3d4
  inputs: {
    "prompt": "Generate a sci-fi spaceship model",
    "style": "realistic",
    "resolution": "2048x2048"
  }
  status: {
    "state": "completed",
    "progress": 100,
    "result": {
      "output_path": "/fake/path/to/result.obj",
      "message": "Fake AIGC job completed successfully"
    }
  }

[17:00:02] [DEBUG   ] [hub.ui.main_window] Displayed aigc/done event for job_a1b2c3d4
[17:00:02] [DEBUG   ] [hub.core.job_center] Cleaning up worker thread
```

**流程说明**：

1. **用户点击按钮** → UI 层
2. **创建 aigc_job 函数** → 包含 AIGC submit + sleep + poll 逻辑
3. **提交到 JobCenter** → 在后台线程异步执行
4. **AIGC Client 调用** → 记录日志，返回假数据
5. **job/done 事件** → JobCenter 发布，包含完整结果
6. **aigc/done 事件** → MainWindow 检测并转发
7. **Console 显示** → 格式化显示 AIGC 任务结果

**成功标志**：
- ✅ UI 不冻结（后台线程工作）
- ✅ 日志完整（从提交到完成）
- ✅ 事件流转（job/done → aigc/done）
- ✅ Console 显示美观（格式化 JSON）
- ✅ 可重复执行（资源正确清理）

**注意事项**：
- 这是 stub 实现，AIGC 服务返回假数据
- 实际 AIGC 集成时需要替换为真实的 HTTP/gRPC 客户端
- 2 秒延迟仅用于演示异步效果
- 真实场景中 AIGC 任务可能需要几分钟
