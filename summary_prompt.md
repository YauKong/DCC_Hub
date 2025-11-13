
请将我们当前项目对话压缩为可交接的“上下文摘要”，用于在新的会话中快速上手。严格使用以下结构与字数上限：

[Project Capsule & Architecture Map]
- 阅读architecture.md
- 记录我们目前在tasks中已完成的进度

[Constraints & Invariants ≤8条]
- 性能/兼容性/版本/风格/安全等不可违背的约束[Decisions Log ≤15条]
- 已拍板决策：决定 → 原因（各一行）

[Open TODO (Next 3) ≤3条]
- 最重要的三个下一步，写成可执行“任务+完成标准”

[Glossary ≤10项]
- 专有名词/缩写 → 一句话定义

[Context Attachments（可选）]
- 代码/文件清单（仅列最关键文件相对路径）
- 重要提示：如需在新会话引用这些文件，请让我@文件

请删除冗余、避免重复、减少形容词，输出干净的Markdown，并保存到和@architecture.md 同级别的位置，以tasks中我们目前已完成的进度 + _summary命名，保持一致性