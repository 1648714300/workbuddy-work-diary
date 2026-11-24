#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
无感工作日记（work-diary）一键安装脚本

功能：
  1. 在目标目录创建 monitor/ 目录结构（logs / screenshots / reports / corpus / tools）
  2. 部署模板与虚构示例文件（纯净版，不含任何真实数据）
  3. 自检：核对目录结构与关键文件完整性
  4. 打印后续步骤（注册 2 个定时自动化 + 安装 skill）

用法：
  python install.py                     # 安装到当前目录
  python install.py --target /some/dir  # 安装到指定目录
  python install.py --force             # 模板文件已存在时强制覆盖
  python install.py --selfcheck-only    # 只跑自检，不安装

幂等：重复运行安全，已存在的文件默认跳过不会被覆盖。
跨平台：Windows / macOS / Linux，仅用标准库。
"""

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
TEMPLATE_DIR = REPO_ROOT / "templates"

DIRS = ["logs", "screenshots", "reports", "corpus", "tools"]

TEMPLATE_MAP = {
    "logs/2026-01-01-示例.md": "logs/2026-01-01-示例.md",
    "logs/ai-watch-2026-01-01-示例.md": "logs/ai-watch-2026-01-01-示例.md",
    "corpus/ai-assistant.md": "corpus/ai-assistant.md",
    "corpus/communication.md": "corpus/communication.md",
    "reports/2026-01-01-总结-示例.md": "reports/2026-01-01-总结-示例.md",
    "reports/工作计划表素材-示例.md": "reports/工作计划表素材-示例.md",
}

TOOLS_README = """tools/ 目录用途说明
====================

这里放本机自行实现的采集辅助脚本（可选）：
- 截屏脚本：无桌面代理能力时，用系统命令截屏（见 docs/porting-guide.md）
- 窗口监视脚本：方式 A 的 AI 生成内容监视 watcher
- Recent/最近文件解析脚本：把最近打开文件的记录转成时间线

注意：本目录随 install.py 创建，脚本内容请按 docs/porting-guide.md 自行部署或从社区获取。
"""


def out(msg: str) -> None:
    print(msg, flush=True)


def install(target: Path, force: bool) -> int:
    monitor = target / "monitor"

    out("")
    out("=" * 62)
    out(" 无感工作日记（work-diary）安装程序")
    out("=" * 62)
    out("")
    out(f"目标目录：{monitor}")
    out("")

    # 1. 目录结构
    created, existed = [], []
    for d in DIRS:
        p = monitor / d
        if p.exists():
            existed.append(d)
        else:
            p.mkdir(parents=True, exist_ok=True)
            created.append(d)
    out(f"[1/4] 目录结构：新建 {len(created)} 个（{', '.join(created) or '无'}），"
        f"已存在 {len(existed)} 个（{', '.join(existed) or '无'}）")

    # 2. 模板与示例
    copied, skipped, missing = 0, 0, []
    for src_rel, dst_rel in TEMPLATE_MAP.items():
        src = TEMPLATE_DIR / src_rel
        dst = monitor / dst_rel
        if not src.exists():
            missing.append(src_rel)
            continue
        if dst.exists() and not force:
            skipped += 1
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied += 1
    out(f"[2/4] 模板与示例：复制 {copied} 个，跳过（已存在）{skipped} 个"
        + (f"，缺失 {len(missing)} 个：{', '.join(missing)}" if missing else ""))

    # 3. tools 说明
    tools_readme = monitor / "tools" / "README.txt"
    if not tools_readme.exists() or force:
        tools_readme.write_text(TOOLS_README, encoding="utf-8")
        out("[3/4] tools/ 说明文件：已写入")
    else:
        out("[3/4] tools/ 说明文件：已存在，跳过")

    # 4. 自检
    ok = selfcheck(monitor)
    out("")
    out("=" * 62)
    if ok:
        out(" 自检通过，安装完成")
    else:
        out(" 自检未通过，请根据上方提示处理后重跑 install.py --selfcheck-only")
    out("=" * 62)
    out("")
    return 0 if ok else 1


def selfcheck(monitor: Path) -> bool:
    out("[4/4] 自检：")
    ok = True
    for d in DIRS:
        p = monitor / d
        status = "通过" if p.exists() else "缺失"
        if not p.exists():
            ok = False
        out(f"      - 目录 {p}: {status}")
    files = [
        ("示例日志", monitor / "logs/2026-01-01-示例.md"),
        ("语料模板", monitor / "corpus/ai-assistant.md"),
        ("示例报告", monitor / "reports/2026-01-01-总结-示例.md"),
        ("示例素材", monitor / "reports/工作计划表素材-示例.md"),
    ]
    for label, p in files:
        status = "通过" if p.exists() else "缺失"
        if not p.exists():
            ok = False
        out(f"      - {label} {p.name}: {status}")

    # 示例文件完整性抽查（含状态标记 / 结构标题）
    sample_log = monitor / "logs/2026-01-01-示例.md"
    if sample_log.exists():
        text = sample_log.read_text(encoding="utf-8", errors="ignore")
        has_marker = "状态：未总结" in text
        has_entry = "## 09:12" in text
        out(f"      - 日志状态标记机制: {'通过' if has_marker else '异常'}")
        out(f"      - 日志采样条目格式: {'通过' if has_entry else '异常'}")
        ok = ok and has_marker and has_entry
    return ok


def print_next_steps() -> None:
    out("")
    out("后续步骤（3 步上线）：")
    out("  1. 安装 skill：把 skill/work-diary/ 整个目录复制到 ~/.workbuddy/skills/（或按平台说明导入），")
    out("     重启会话后 AI 即可在每日总结任务中自动遵循本体系流程。")
    out("  2. 注册「操作采样」自动化：prompt 复制自 prompts/automation-sampling.md，")
    out("     替换 <监控根目录> 为实际路径，频率设为工作日整点。")
    out("  3. 注册「每日总结」自动化：prompt 复制自 prompts/automation-daily-summary.md，")
    out("     频率设为每天 16:00（周一会自动追加工作计划表素材）。")
    out("")
    out("可选：AI 生成内容监视见 prompts/automation-ai-watch.md（方式 A watcher / 方式 B 并入采样）。")
    out("提示：示例文件内容全部虚构，看懂格式后可删除；templates/ 同名文件不会被覆盖。")
    out("")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="无感工作日记一键安装")
    parser.add_argument("--target", default=".", help="安装目标目录（默认当前目录）")
    parser.add_argument("--force", action="store_true", help="覆盖已存在的模板/示例文件")
    parser.add_argument("--selfcheck-only", action="store_true", help="只跑自检不安装")
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    monitor = target / "monitor"

    if args.selfcheck_only:
        ok = selfcheck(monitor)
        out("")
        out("自检结果：" + ("通过" if ok else "未通过"))
        return 0 if ok else 1

    code = install(target, args.force)
    if code == 0:
        print_next_steps()
    return code


if __name__ == "__main__":
    sys.exit(main())
