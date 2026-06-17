# My Hermes Bootstrap

这个仓库用于保存 Hermes Agent 的自举说明、环境变量模板和参考资料，方便在重装系统、新设备或环境丢失后快速恢复运行环境。

## 仓库内容

- `SKILL.md`：完整的 Hermes Bootstrap 技能说明，包含恢复流程和执行约束。
- `reference/env-template.md`：环境变量模板，用于生成本地配置文件。

## 使用方式

1. 阅读 `SKILL.md`，确认恢复流程和高风险操作。
2. 参考 `reference/env-template.md`，在仓库根目录创建本地文件 `my-hermes-bootstrap.env` 并填入真实配置。
3. 按 `SKILL.md` 中的顺序执行环境恢复，包括代理、模型、消息渠道、外部记忆、Skill 和插件安装。
4. 执行 `hermes doctor` 做最终验证。

## 本地配置约定

- `my-hermes-bootstrap.env` 仅用于本地保存敏感配置，不提交到 Git。
- 仓库中只保留模板文件，不保留真实密钥、令牌或账户信息。
- 如需共享新增变量，请先更新 `reference/env-template.md`。

## 建议流程

- 在新机器上先安装基础依赖：`python3`、`pip3`、`git`、`ffmpeg`、`npm`。
- 恢复前先备份已有的 `~/.hermes/.env` 和 `SOUL.md`。
- 访问 GitHub 或安装 Skill 前先确认代理和 `GITHUB_TOKEN` 可用。

## 注意事项

- `SKILL.md` 中的环境变量合并逻辑是增量覆盖，不应直接整体覆盖已有 `~/.hermes/.env`。
- 如果需要新增恢复步骤，优先更新 `SKILL.md`，保持 README 只承担仓库导航和快速上手职责。