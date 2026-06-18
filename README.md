# My Hermes Bootstrap

起初，只是为了方便我迁移和重装 Hermes Agent，便于我快速完成重建。

## 仓库内容

- `SKILL.md`：完整的 Hermes Bootstrap 技能说明，包含执行流程和执行约束。
- `my-hermes-bootstrap.env`：当前环境的实际配置文件快照（由脚本生成）。
- `my-hermes-bootstrap.env.template`：环境变量模板（纯 .env 格式），内含默认值，可手动复制编辑。
- `resource/`：Hermes 未安装时的回退来源，包含 `.env` 和 `config.yaml` 两份参考文件。
- `script/generate_bootstrap_env.py`：环境变量生成脚本，自动从 Hermes 安装目录（`~/.hermes/.env` + `~/.hermes/config.yaml`）提取配置，Hermes 未安装时回退到 `resource/`。

## 使用前必读
该 `SKILL.md` 中包含高风险操作，可能修改 Hermes Agent 的基础配置并破坏原有配置，请慎重使用。

**安全说明：**
- `my-hermes-bootstrap.env` 是本地生成的快照，可能包含真实 API Key/Secret/环境地址，已被 `.gitignore` 排除，**禁止提交**。
- `resource/.env` 与 `resource/config.yaml` 是回退参考文件，**不应包含真实凭据**，目前已清空为占位值。
- 已确认 Git 历史中没有提交过包含敏感数据的 `.env` 或 `config.yaml` 文件。

详细阅读 `SKILL.md`，确认执行流程和高风险操作。根据你的需求，可修改 `SKILL.md` 让 AI 执行，或者手动执行。

**备份！备份！备份！**

> 由 AI 执行 `SKILL.md` 存在不可控风险，一定要提前备份。

```bash
hermes update --backup
```

## 使用方式

### Step 1: 阅读 `SKILL.md`，确认执行流程和高风险操作。
### Step 2: 配置 env

#### 从模板生成新的 env
根据模板 `./my-hermes-bootstrap.env.template` 生成 `./my-hermes-bootstrap.env`，并手动填入参数。

#### 从已有的 Hermes Agent 提取 env

**默认使用:**
自动检测 Hermes 安装目录（`~/.hermes/.env` + `~/.hermes/config.yaml`），未安装则回退到 `resource/`。输出到仓库根目录的 `my-hermes-bootstrap.env`：
```bash
python script/generate_bootstrap_env.py
```

**自定义输入输出:**
```bash
python script/generate_bootstrap_env.py --source <env-path> --config <config-path> --output <target-path>
```

### Step 3: 执行

#### 让 Hermes Agent 执行（推荐）
1. 手动配置 Hermes Agent 使用模型。
2. 启动 Hermes CLI，让 Hermes 帮你执行：
```
请完整阅读 ./my-hermes-bootstrap/SKILL.md，然后完成初始化配置。
```

#### 手动执行
按 `SKILL.md` 中的顺序执行环境恢复，包括代理、模型、消息渠道、外部记忆、Skill 和插件安装。

### Step 4: 验证

```bash
hermes doctor
```

## 完整示例

### 新安装 Hermes Agent（参考 [Hermes Agent 官网安装指导](https://hermes-agent.nousresearch.com/docs/zh-Hans/getting-started/installation)）

```bash
# 如需代理，请先按你的环境设置代理
export HTTP_PROXY=<your-http-proxy>
export HTTPS_PROXY=<your-https-proxy>
export ALL_PROXY=<your-all-proxy>
export NO_PROXY=localhost,127.0.0.1,::1

# 以非特权服务用户身份，运行常规安装程序。它会检测到缺少 sudo，跳过 --with-deps，并将 Chromium 安装到用户本地的 Playwright 缓存中：
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

# 如果想完全跳过 Playwright 步骤——例如在无头环境中运行且不需要浏览器自动化——传入 --skip-browser：
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-browser

# 添加到服务用户的 profile
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

### 故障记录

```
× Failed to build `hermes-agent @ file:///vol3/1001/yosephine/.hermes/hermes-agent`
  ├─▶ Failed to read metadata: `/vol3/1001/yosephine/.cache/uv/builds-v0/.tmpnUYo5j/hermes_agent-0.16.0-0.editable-py3-none-any.whl`
  ╰─▶ No .dist-info directory found
```

### 原因

`/vol3/` 是一个 NFS 网络存储卷，Hermes 的源码和 uv 构建缓存都放在 NFS 上，这是根本原因。
NFS 上 `rename()` 原子操作不可靠，临时目录 `.tmpnUYo5j` 没有被正确 `mv` 到最终位置，导致 `.dist-info` 目录丢失。

### 解决方案

将 uv 缓存目录切换到非 NFS 存储卷：

```bash
export UV_CACHE_DIR=/home/yosephine/hermes-uv-cache
```