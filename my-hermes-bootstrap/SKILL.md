---
name: my-hermes-bootstrap
description: 重新安装或新环境快速配置 Hermes Agent 的一站式指南，只有用户主动要求调用此技能时才会执行，适合在环境丢失、重装系统或新设备上快速恢复 Hermes 运行环境。
---

# My Hermes Bootstrap

## 用途

用于快速恢复或初始化 Hermes Agent 运行环境，从环境变量、模型配置到消息渠道、记忆后端、Skill 安装、人格文件一步到位。

## 执行步骤

### Step 1: 检查依赖
[ ] `./my-hermes-bootstrap.env` 文件存在且非空

### Step 2: 规划步骤
- 必须完整阅读本文档，理解每个步骤的目的和操作细节。
- 必须完整读取并理解 `my-hermes-bootstrap.env` 中的环境变量，确保所有必需的变量都已正确设置。
- 规划即将要做的动作，标注高风险操作，输出给用户，得到确认后再执行。

### Step 3: 确定 SOUL.md 写入路径

Hermes 的人设文件路径取决于当前 profile，按以下优先级确定：

| 条件 | SOUL.md 路径 |
|------|-------------|
| 使用非 default profile | `$HERMES_HOME/profiles/<profile>/SOUL.md` |
| 默认（无 profile） | `$HERMES_HOME/SOUL.md` |

其中 `HERMES_HOME` 默认为 `~/.hermes`。

```bash
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
ACTIVE_PROFILE="${HERMES_PROFILE:-default}"

# 如果 default 且 ~/.hermes/SOUL.md 已存在，直接用
if [[ "$ACTIVE_PROFILE" == "default" && -f "$HERMES_HOME/SOUL.md" ]]; then
  SOUL_FILE="$HERMES_HOME/SOUL.md"
else
  SOUL_FILE="$HERMES_HOME/profiles/$ACTIVE_PROFILE/SOUL.md"
fi

mkdir -p "$(dirname "$SOUL_FILE")"
echo "SOUL_FILE=$SOUL_FILE"
```

[ ] 执行上方脚本，确认输出的 `SOUL_FILE` 路径正确

### Step 4: 备份并写入 SOUL.md
[ ] 备份 `~/.hermes/.env` 到 `~/.hermes/.env.bak`（如果存在）
[ ] 备份 `$SOUL_FILE` 到 `$SOUL_FILE.bak`（如果存在）

```bash
if [[ -f ~/.hermes/.env ]]; then
  cp ~/.hermes/.env ~/.hermes/.env.bak
fi

if [[ -f "$SOUL_FILE" ]]; then
  cp "$SOUL_FILE" "$SOUL_FILE.bak"
fi
```

将以下内容写入 Step 3 解析出的 `$SOUL_FILE`，覆盖原文件内容。
```
# Yosephine

## 角色定义
你是"约瑟芬妮"(Yosephine)，是Yosef的AI操作员和思考搭档，理解Yosef的意图，然后完成相应工作，主动发现问题、提出建议、推进工作、输出可靠结论。

## 沟通风格
- 必须用中文回复
- 对用户的输入必须先分析用户的情绪，然后用适合的语气来回复
- 对用户的输入内容存疑时，必须询问用户的意图，确保理解了用户的输入内容和意图
- 对话感：默认使用第二人称"你"，追求穿透力而非机械的说教。

## 思考模式
你必须理解Yosef的输入内容，然后进行内容分类。你可以增加和修改 `分类描述`、`执行要点`、`回复内容必须遵循`，用于提升你的服务质量。
| 分类描述 | 执行要点 | 回复内容必须遵循 |
| --- | --- | --- |
| 日常对话 | 分析用户情绪 | 有强烈的对话感、必要时增加emoji |
| 问题咨询 | 搜索和调研必须要可信、必须至少对你的结论进行两次论证 | 包含置信度评分、标注引用来源、结论先行、允许反驳 |
| 执行简单任务 | 必须规划执行步骤、自主执行步骤 | 反馈最终结果，禁止包含每个步骤的执行结果 |
| 执行复杂任务 | 必须调用skill grill-me、必须规划执行步骤、必须让用户确认执行步骤 | 结论先行、每个步骤都必须用一句话描述执行结果 |
| 编码任务 | 必须调用skill grill-me、必须规划执行步骤、必须让用户确认执行步骤、必须调用OpenCode执行编码任务、必须对产出进行验证和测试、必须做一次优化代码的操作 | 结论先行、必须包含对代码质量的评分、必须包含验证结果、必须包含用途和功能的描述 |

## 反驳规则
当你认为Yosef的方向有问题时，直接说出来。但每个反对意见必须有依据：数据、例子、推理过程。为了反对而反对等于浪费时间。因为能证明某个方案会失败而反对，是必要的。

## 必须遵守
- 当生成任何skill时，必须让Yosef确认skill的功能和用途，禁止生成未经确认的skill
- 当需要将对话写入记忆时，必须让Yosef确认写入的内容和用途，禁止未经确认就写入记忆
```

### Step 5: 配置代理
为Hermes Agent配置代理为 `http://10.0.0.10:9132`，并验证代理访问Github正常。后续步骤按需使用代理，如访问Github API、安装Skill等。
```bash
hermes config set proxy.http http://10.0.0.10:9132
hermes config set proxy.https http://10.0.0.10:9132
hermes config set proxy.no_proxy "localhost,127.0.0.1,10.0.0.0/8,::1"
```

### Step 6: 合并环境变量（禁止直接覆盖）
```bash
# ✅ 正确：逐行合并，同键覆盖，差异追加
merge_env() {
  local src="$1" dst="$2"
  while IFS='=' read -r key val; do
    [[ -z "$key" || "$key" == \#* ]] && continue
    if grep -q "^${key}=" "$dst" 2>/dev/null; then
      sed -i "s|^${key}=.*|${key}=${val}|" "$dst"
    else
      echo "${key}=${val}" >> "$dst"
    fi
  done < "$src"
}
merge_env ./my-hermes-bootstrap.env ~/.hermes/.env
source ~/.hermes/.env
```

### Step 7: 检查并安装依赖
检查下述依赖是否存在，如不存在，则安装。
```bash
command -v python3 pip3 git ffmpeg npm
```

### Step 8: 配置模型

```bash
source ~/.hermes/.env
hermes config set model.provider deepseek
hermes config set model.model deepseek-v4-flash
hermes config set model.api_key "$DEEPSEEK_API_KEY"

# Vision 辅助模型
hermes config set auxiliary.vision.provider openrouter
hermes config set auxiliary.vision.model google/gemini-2.5-flash
hermes config set auxiliary.vision.api_key "$OPENROUTER_API_KEY"

# TTS 语音
hermes config set tts.provider mimo
hermes config set tts.api_key "$XIAOMI_API_KEY"
hermes config set stt.enabled false
```

### Step 9: 配置消息渠道

**飞书（Feishu）：**
```bash
source ~/.hermes/.env
hermes config set feishu.app_id "$FEISHU_APP_ID"
hermes config set feishu.app_secret "$FEISHU_APP_SECRET"
hermes config set feishu.domain "$FEISHU_DOMAIN"
hermes config set feishu.connection_mode "$FEISHU_CONNECTION_MODE"
hermes config set feishu.allow_all_users "$FEISHU_ALLOW_ALL_USERS"
hermes config set feishu.group_policy "$FEISHU_GROUP_POLICY"
hermes config set feishu.home_channel "$FEISHU_HOME_CHANNEL"
```

**微信（WeChat）：**
```bash
source ~/.hermes/.env
hermes config set weixin.account_id "$WEIXIN_ACCOUNT_ID"
hermes config set weixin.token "$WEIXIN_TOKEN"
hermes config set weixin.base_url "$WEIXIN_BASE_URL"
hermes config set weixin.cdn_base_url "$WEIXIN_CDN_BASE_URL"
hermes config set weixin.dm_policy "$WEIXIN_DM_POLICY"
hermes config set weixin.allow_all_users "$WEIXIN_ALLOW_ALL_USERS"
hermes config set weixin.group_policy "$WEIXIN_GROUP_POLICY"
hermes config set weixin.home_channel "$WEIXIN_HOME_CHANNEL"
```

### Step 10: 配置外部记忆（OpenViking）

OpenViking 服务的验证路径是 `/health`：

```bash
source ~/.hermes/.env
curl -s --connect-timeout 5 "${OPENVIKING_ENDPOINT}/health"
# 期望 HTTP 200

hermes config set memory.provider openviking
hermes config set openviking.endpoint "$OPENVIKING_ENDPOINT"
hermes config set openviking.api_key "$OPENVIKING_API_KEY"
hermes config set openviking.account "$OPENVIKING_ACCOUNT"
hermes config set openviking.user "$OPENVIKING_USER"
hermes config set openviking.agent "$OPENVIKING_AGENT"
```

### Step 11: 安装 Skill

[ ] 检查 `GITHUB_TOKEN` 是否生效，是否能正常访问Github API（如 `curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/rate_limit` 返回正常结果）

1. 先配置代理环境变量，确保后续访问 GitHub API 和下载 Skill 不受限。
```bash
source ~/.hermes/.env
export http_proxy=http://10.0.0.10:9132
export https_proxy=http://10.0.0.10:9132
```
2. 初始化 Skills Hub：`hermes skills list`

3. 先尝试从 Hub 安装以下 Skill，失败则回退到 raw URL 安装
- skills-sh/vercel-labs/skills/find-skills
  - raw URL: https://raw.githubusercontent.com/vercel-labs/skills/main/skills/find-skills/SKILL.md
- skills-sh/mattpocock/skills/grill-me
  - raw URL: https://raw.githubusercontent.com/mattpocock/skills/main/skills/productivity/grill-me/SKILL.md
- feisou/skills/feisou-search
  - feisou-search 不在 Hub 上，需要直接从 raw URL 安装
  - raw URL: https://raw.githubusercontent.com/feisou/skills/main/skills/feisou-search/SKILL.md

```bash
source ~/.hermes/.env

# 从 Hub 安装，失败则从 raw URL 安装
yes | hermes skills install "skills-sh/vercel-labs/skills/find-skills" 2>&1 \
  || yes | hermes skills install "https://raw.githubusercontent.com/vercel-labs/skills/main/skills/find-skills/SKILL.md"

yes | hermes skills install "skills-sh/mattpocock/skills/grill-me" 2>&1 \
  || yes | hermes skills install "https://raw.githubusercontent.com/mattpocock/skills/main/skills/productivity/grill-me/SKILL.md"

yes | hermes skills install "https://raw.githubusercontent.com/feisou/skills/main/skills/feisou-search/SKILL.md"
```

### Step 12: 安装插件
根据需要安装以下插件，如 `hermes plugins install <plugin-name>`，并按照插件文档进行配置。
- rtk
  - GitHub: https://github.com/rtk-ai/rtk
  - 终端执行: `rtk init --agent hermes`
- hermes-lark-streaming
  - GitHub: https://github.com/Aowen-Nowor/hermes-lark-streaming

### Step 13: 最终验证
```bash
hermes doctor
```

### Step 14: 可选集成 — OpenCode（AI 编码代理）

OpenCode 是一个开源的 AI 编码代理，提供 Web 界面、TUI 终端和 IDE 扩展。参考官方文档：https://opencode.ai/docs/zh-cn

1. 必须使用安装脚本安装opencode，禁止使用npm安装。
```bash
export http_proxy=http://10.0.0.10:9132
export https_proxy=http://10.0.0.10:9132
curl -fsSL https://opencode.ai/install | bash
```
2. 验证安装成功：`opencode --version`

## 参考文件
- `reference/env-template.md` — 环境变量模板
