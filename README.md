# Beautiful Obsidian Canvas

面向 Codex 和 Claude Code 的 Obsidian Canvas 画板技能。它使用原生 [JSON Canvas 1.0](https://jsoncanvas.org/spec/1.0/) 创建、换风格和整理可编辑的 `.canvas` 文件，不依赖 CSS、社区插件或特定 Vault 配置。

技能内置 35 款视觉风格和 6 种叙事布局。生成画板时会先梳理节点之间的真实关系，再通过对齐、分组、路由汇聚节点和留白减少连线交叉，而不是为了整洁删除必要连接。

## 主要能力

- 创建架构图、流程图、时间线、对比矩阵、中心辐射图、看板和系统地图。
- 为新画板推荐风格与布局，并在用户选择后再生成。
- 在不改变内容和结构的前提下切换已有画板风格。
- 整理节点对齐、尺寸、间距、文字容量和分组边界。
- 审核连线语义，减少交叉、穿越节点和不必要的高连接度。
- 校验 JSON Canvas 字段、节点 ID、边引用、重叠、文字溢出和连线质量。
- 通过 Obsidian CLI 打开画板并生成截图，用于最终视觉检查。

完整风格列表见 [references/CATALOG.md](references/CATALOG.md)，布局模板见 [references/LAYOUTS.md](references/LAYOUTS.md)。

## 依赖

- Python 3.9 或更高版本。
- 使用画板校验功能时不需要额外 Python 依赖。
- 使用自动打开和截图功能时，需要：
  - 已安装并运行 Obsidian；
  - 已在 Obsidian 设置中启用 CLI；
  - 已启用 Canvas 核心功能；
  - 目标 `.canvas` 文件位于已注册的 Vault 中。

仅生成或修改 JSON Canvas 文件时，Obsidian CLI 不是必需条件。

## 安装

### 安装到共享技能目录

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/SawyerPan/beautiful-obsidian-canvas.git \
  ~/.agents/skills/beautiful-obsidian-canvas
```

Codex 和 Claude Code 可以共用这个目录，避免维护重复的技能副本。如果你的 Agent 客户端使用其他技能目录，请将其配置或链接到该共享位置。

### 更新技能

```bash
git -C ~/.agents/skills/beautiful-obsidian-canvas pull --ff-only
```

## 使用示例

```text
$beautiful-obsidian-canvas 为 AI SaaS 产品创建一张分层技术架构图
$beautiful-obsidian-canvas 把这张画板换成 Linen Cut 风格，保留布局和连线
$beautiful-obsidian-canvas 整理已有画板的对齐、文字和连线，保持语义关系不变
```

对于新画板和完整换风格，技能会提供三款适合当前内容的风格选择；存在多种合理布局时，也会先提供布局选项。

## 脚本

检查本机环境和目标画板：

```bash
bash scripts/preflight.sh /path/to/board.canvas
```

校验画板：

```bash
python3 scripts/validate_canvas.py /path/to/board.canvas --strict
```

打开画板并生成截图：

```bash
bash scripts/open_and_snapshot.sh \
  /path/to/board.canvas \
  /path/to/preview.png
```

## 设计原则

- 语义正确优先于视觉对称；不为减少连线而删除真实依赖。
- 普通节点总连接数默认不超过 4，明确的语义汇聚节点最多可达到 6。
- 主方向统一，目标是零连线交叉、零连线穿越无关节点。
- 同级节点严格对齐，并复用一致的尺寸、间距和组内边距。
- 只使用 JSON Canvas 原生字段，画板保持可编辑和可移植。

## 目录结构

```text
beautiful-obsidian-canvas/
├── SKILL.md
├── README.md
├── LICENSE
├── agents/
│   └── openai.yaml
├── references/
│   ├── CATALOG.md
│   ├── LAYOUTS.md
│   ├── RULES.md
│   └── styles/
└── scripts/
    ├── open_and_snapshot.sh
    ├── preflight.sh
    └── validate_canvas.py
```

## 来源与许可

本项目采用 [MIT License](LICENSE)。视觉风格名称与配色说明改编自 Zara Zhang 的 [beautiful-feishu-whiteboard](https://github.com/zarazhangrui/beautiful-feishu-whiteboard)，对应来源提交为 [`6989843b`](https://github.com/zarazhangrui/beautiful-feishu-whiteboard/commit/6989843b355ac92ebbd4f66166189a001e61e9b5)。完整署名与改编声明见 [LICENSE](LICENSE)。
