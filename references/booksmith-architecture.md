# Sloth-BookSmith-Den — 排版引擎架构分析（2026-05-17）

来源：git clone + 读 SKILL.md + README.md + booksmith.py（1,980行）

## 定位

匠书·出版排版引擎。不是写作工具，是排版工具。将 Markdown/Word 书稿转换为出版级电子书。

## 核心架构

```
Markdown/Word → 解析 → 主题应用 → HTML/CSS构建 → Paged.js渲染 → PDF/HTML/ePub/MOBI/AZW3
```

## 关键能力

### 1. 主题系统（6套 YAML 预设）
- publishing-classic / academic-serif / tech-modern / consulting-navy / literary-minimal / dark-ebook
- 每套定义：字体、字号、颜色、间距、边距
- 位置：presets/*.yaml

### 2. 字体系统（三平台自动检测）
- macOS: Songti SC/PingFang SC/Menlo
- Windows: SimSun/Microsoft YaHei/Consolas
- Linux: Noto CJK/DejaVu Sans Mono
- 函数：detect_fonts()

### 3. 排版能力
| 能力 | 说明 |
|------|------|
| 首行缩进 2em | 正文段落 |
| 行距 1.75 | 正文 |
| 段间距 0.5em | |
| 页眉页脚 | 左页书名 + 右页章名，页码居中 |
| 首字下沉 | 可选 |
| 避头尾 | CJK断行 |
| 交叉引用 | 识别参见/参阅/见 |
| 子章节导航 | H2锚点+PDF书签 |
| 代码高亮 | Pygments |
| 水印 | CLI参数注入 |
| 图片处理 | 居中+图注 |

### 4. 多格式输出
PDF（Playwright+Paged.js）/ HTML / ePub / MOBI / AZW3

### 5. 封面系统
5种版式：solid/gradient/image/texture/academic

### 6. 质量检查（17项自动验证）
封面/版权页/目录/扉页/缩进/页眉/页码/图片/表格/代码/引用/锚点/widows

## 与我的 build-pdf-press.py 对比

| | BookSmith-Den | 我的脚本 |
|--|--------------|---------|
| 行数 | 1,980 | 293 |
| 主题 | 6套YAML | 硬编码CSS |
| 字体 | 三平台自动检测 | 手写 |
| 页眉页脚 | ✅ | ❌ |
| 首字下沉 | ✅ | ❌ |
| 交叉引用 | ✅ | ❌ |
| 子章节导航 | ✅ | ❌ |
| 多格式 | PDF/HTML/ePub/MOBI/AZW3 | 仅PDF |
| 封面 | 5种版式 | 文字占位 |
| Paged.js | ✅ | ❌ |
| 质量检查 | 17项 | ❌ |

## 使用方式

```bash
cd ~/Desktop/Sloth-BookSmith-Den
python scripts/booksmith-cli.py --input manuscript.md --theme tech-modern --format pdf
```

## 依赖
markdown / pygments / pymupdf / playwright / pyyaml / python-docx

## 关键教训

1. 排版是门专业活，293行不可能替代1,980行
2. YAML主题配置比硬编码CSS更灵活
3. Paged.js是CSS分页渲染的事实标准
4. 多格式输出需要不同渲染路径
5. 好排版 = 字体 × 间距 × 版式 × 封面，四个维度缺一不可
