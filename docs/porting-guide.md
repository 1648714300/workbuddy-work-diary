# 非 WorkBuddy 平台移植说明

本体系的设计是平台无关的：采集层攒证据、总结层读证据写报告。强依赖只有两个——**定时调度**和**截屏**。其他 AI 助手（Claude Code、Cursor、各类 Agent 框架）或纯脚本方案都能实现。

## 需要移植的四项能力

### 1. 定时调度

| 平台 | 方案 |
|------|------|
| Windows | `schtasks /create /tn "work-sampling" /tr "python capture.py" /sc hourly`（或任务计划程序 GUI） |
| macOS / Linux | cron：`0 8-16 * * 1-5 python3 capture.py`；launchd / systemd timer 亦可 |
| 有 Agent 框架 | 框架自带 scheduler / cron 功能直接用，prompt 取自 `prompts/` 目录 |

调度两个任务即可：采样（工作日整点）、总结（每天 16:00，判断当天为周一时执行附加步骤）。

### 2. 截屏

| 平台 | 方案 |
|------|------|
| Windows | PowerShell：`Add-Type` 调 System.Drawing 截全屏；或 `nircmd savescreenshot` |
| macOS | `screencapture -x ~/monitor/screenshots/...png` |
| Linux | `gnome-screenshot -f` / `scrot` / `import -window root`（ImageMagick） |

存到 `monitor/screenshots/YYYY-MM-DD/HH-MM.png`，分辨率与大小写进日志。

### 3. 最近文件痕迹（时间线兜底证据源）

| 平台 | 方案 |
|------|------|
| Windows | Recent 文件夹 `%APPDATA%\Microsoft\Windows\Recent` 的 .lnk 修改时间，可用 pywin32 解析目标路径 |
| macOS | `defaults read com.apple.recentitems` 或 `ls -lt ~/Library/Application Support/...`；`mdls` 可查具体文件 |
| Linux | `~/.local/share/recently-used.xbel`（XDG 标准，GTK 应用通用） |

输出格式统一为「时刻 + 文件名」列表，写进日志「活动痕迹」字段。这是采样漏掉时的关键兜底——截不到屏也能还原大概时间线。

### 4. AI 生成内容监视（可选）

- 有窗口枚举能力：监视 AI 面板窗口标题（如含「AI」「助手」等关键词），命中即按分钟截图留档（方式 A）
- 无窗口枚举：退化为每次采样时检查截屏中是否有 AI 面板（方式 B），由总结任务从截图转录
- 独立的桌面 AI 应用（如各类助手面板）也可直接读其本地历史文件/导出记录

## 总结任务的移植

总结层是纯「读文件 + 写报告」，任何能读写文件系统的 AI 助手都能跑：

1. 把 `skill/work-diary/SKILL.md` 的流程改写为对应平台的 system prompt / 规则文件
2. `skill/work-diary/references/report-spec.md` 的报告结构与写作规范原样可用
3. 派生自动化的规则（查重、试跑、转正）按所用平台的定时任务 API 对应实现；没有自动化 API 时输出「建议人工创建的任务清单」代替

## 纪律清单（移植后逐条自查）

- [ ] 采集全程只读，不移动/删除/重命名任何用户文件
- [ ] 截屏失败时降级为只记痕迹，不中断
- [ ] 报告每条结论有出处；Recent 补的段落标「未采到画面，按 Recent 痕迹」
- [ ] 无采样日写「今日无采样」，不编造
- [ ] 状态标记机制（未总结/已总结）正常运转，失效时兜底并提示
- [ ] 语料只记用户本人发起/确认的内容
- [ ] 新自动化先查重、先试跑、后转周期；skill/风格蒸馏等用户确认后才建
