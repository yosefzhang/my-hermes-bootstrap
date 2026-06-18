# AGENTS.md — my-hermes-bootstrap

## Repository Overview

Hermes Agent 环境快速恢复/初始化工具包。在新机器、重装系统或环境丢失后，一键重建 Hermes Agent 运行环境。

## Directory Structure

```
my-hermes-bootstrap/
├── AGENTS.md                         # 本文件 — AI 助手行为指南
├── README.md                         # 使用说明
├── SKILL.md                          # Hermes Agent 技能定义（14 步自动化引导脚本）
├── my-hermes-bootstrap.env           # 当前环境配置快照（由脚本自动生成，含敏感凭证）
├── my-hermes-bootstrap.env.template  # 环境变量模板（.env 格式，手动编辑用）
├── resource/
│   ├── .env                          # Hermes 未安装时的回退 .env（含详细注释）
│   └── config.yaml                   # Hermes 未安装时的回退 config.yaml
└── script/
    └── generate_bootstrap_env.py     # 从 ~/.hermes 自动提取配置并生成 .env
```

## Key Files

| File | Purpose |
|------|---------|
| `SKILL.md` | 核心文件。Hermes Agent 的 Skill 定义，包含完整的 14 步引导流程。修改此文件前需确认不会破坏执行流程。 |
| `my-hermes-bootstrap.env` | 运行时配置快照，**包含明文 API Key/Secret**。禁止提交到公开仓库。 |
| `my-hermes-bootstrap.env.template` | 模板文件，键名与脚本中的 `CONFIG_TO_ENV` 和 `PROXY_KEY_ALIASES` 保持一致。 |
| `script/generate_bootstrap_env.py` | 负责从 `~/.hermes/.env` + `~/.hermes/config.yaml` 提取配置并渲染模板。Hermes 未安装时回退到 `resource/`。仅标准库 + PyYAML 依赖。 |
| `resource/config.yaml` | 回退配置文件。内容需与 Hermes Agent 的实际 `config.yaml` 格式兼容（`_config_version` 字段标记版本）。 |

## Workflows

### 生成 env 快照

```bash
python script/generate_bootstrap_env.py
# 自定义输入输出:
python script/generate_bootstrap_env.py --source <env-path> --config <config-path> --output <target-path>
```

### 执行引导

由 Hermes Agent 读取 `SKILL.md` 后自动执行，或按 `SKILL.md` 步骤手动执行。

### 验证

```bash
hermes doctor
```

## Coding Conventions

### Python (`script/`)

- Python 3.10+ type hints (`from __future__ import annotations`)
- `pathlib.Path` 代替 `os.path`
- 无外部依赖（除 `PyYAML`，仅用于解析 config.yaml）
- `.env` 解析容忍 BOM（`utf-8-sig`）、`export ` 前缀、空行、注释
- 模板渲染是纯文本替换，非 Jinja2 等模板引擎
- 脚本以 `raise SystemExit(main())` 退出

### SKILL.md

- 遵循 Hermes Agent Skill 规范（frontmatter 中有 `name`、`description` 字段）
- 每个步骤前有 `[ ]` 复选框标记完成状态
- 高风险操作（备份、覆盖文件）必须提前输出给用户确认
- `source ~/.hermes/.env` 出现在每个配置步骤前，确保环境变量可用

## Environment Variables

所有敏感信息通过 `.env` 文件管理，**绝不硬编码到脚本中**。

### 关键变量命名规范

| 前缀/域 | 用途 |
|---------|------|
| `DEEPSEEK_*`, `OPENROUTER_*` | LLM API Key |
| `FEISHU_*` | 飞书消息渠道 |
| `WEIXIN_*` | 微信消息渠道 |
| `OPENVIKING_*` | 外部记忆后端 |
| `TAVILY_*` | 搜索 API |
| `GITHUB_TOKEN` | GitHub API（Skills Hub 安装用） |
| `FEISOU_*` | Feisou 搜索 Skill |

### Config.yaml 映射

脚本 `CONFIG_TO_ENV` 将 `config.yaml` 字段映射为 env 变量名：

| config path | env var |
|---|---|
| `memory.write_approval` | `MEMORY_WRITE_APPROVAL` |
| `skills.write_approval` | `SKILLS_WRITE_APPROVAL` |
| `display.language` | `DISPLAY_LANGUAGE` |

## Testing & Validation

- 无自动化测试框架
- 验证方式：`hermes doctor`
- `generate_bootstrap_env.py` 的验证：手动运行确认输出文件正确

## Safety & Security

- **不要在 AI 对话中泄漏 `.env` 内容**（含大量明文 API Key）
- **不要将 `my-hermes-bootstrap.env` 提交到公开仓库**
- `resource/.env` 与 `resource/config.yaml` 是回退参考文件，**不应包含真实凭据或环境专属配置**（如内网 IP）。
- 修改 `SKILL.md` 时注意备份步骤（Step 4 的 `.bak` 文件）
- 所有高风险操作必须在执行前让用户确认（参考 SKILL.md Step 2）
- 模板文件 `my-hermes-bootstrap.env.template` 是安全的（不含真实凭据），可以提交
