# 自动化 prompt：AI 生成内容监视（可选）

适用场景：用户常使用 AI 办公助手（如 WPS 灵犀、AI 文档/AI PPT 面板）生成内容，希望把生成物沉淀成语料库，日后蒸馏为个人风格 skill。

两种实现方式，二选一：

## 方式 A：独立 watcher（推荐，适合高频使用 AI 面板的用户）

不占用自动化额度，用本机常驻脚本监视窗口标题命中并按分钟截图留档：

- 监视窗口标题关键词（如「灵犀」「AI 文档」「AI PPT」等，按实际面板修改）
- 命中即截图到 `monitor/screenshots/ai-watch/YYYY-MM-DD/HH-MM-SS.png`
- 追加留档 `monitor/logs/ai-watch-YYYY-MM-DD.md`，格式：

```
## HH:MM:SS｜未转录
- 命中窗口：<窗口标题>
- 截图：screenshots/ai-watch/YYYY-MM-DD/HH-MM-SS.png（大小）
```

- 「未转录」条目由每日总结任务读取截图、把生成内容转录进 `monitor/corpus/<渠道名>.md` 后改为「已转录」
- 参考实现可参照「操作采样」自动化的截屏能力；无桌面代理时可用系统截屏命令 + 窗口枚举脚本实现

## 方式 B：并入采样自动化（通用，零额外配置）

在 `prompts/automation-sampling.md` 的第 3 步已内置：每次采样时检查 AI 助手面板，有生成内容则摘记要点并按会话追加 `monitor/corpus/<渠道名>.md`，格式：

```
## YYYY-MM-DD HH:MM｜<主题>
- 来源：<哪个 AI 面板/会话>
- 类型：<文书起草/表格/汇报材料/翻译/其他>
- 内容摘记：<代表性段落，保留原话>
- 质量点评：<可取处/问题处，一句>
```

## 语料文件约定

- 每个来源渠道一个文件：`monitor/corpus/lingxi.md`、`diantouyi.md`、`weixin.md`……（按实际使用命名）
- 文件头部注明「累计条数由每日总结任务统计，达到阈值（默认 20 条）后提案蒸馏风格 skill」
- 只采集用户自己生成/确认过的内容；别人发来的消息不采集
