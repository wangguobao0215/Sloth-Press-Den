# Book Illustration Workflow — 手绘风格配图生成管线

> 适用于 sloth-press-den 商业畅销书的章节配图。
> 生成手绘风格概念插图，插入 merged-manuscript.md 后构建PDF。

---

## 核心原则

1. **不用AI生图API** — 当前设备无ComfyUI/Stability/Replicate等可用，同时AI生图中文文字渲染不可靠。用 **HTML+CSS 手绘风格 + Playwright 截图** 代替。
2. **CSS手绘效果三要素**：
   - `feTurbulence + feDisplacementMap` SVG滤镜 → 模拟铅笔抖动/不规则边缘
   - 暖色纸张底色（#F5F0E8）+ 斑驳纹理 → 模拟纸面质感
   - 手写字体（`Ma Shan Zheng`, `ZCOOL KuaiLe`）+ 轻微旋转/倾斜 → 模拟手绘不完美感
3. **每章一张概念图** — 不是内容图解，是**核心矛盾的视觉隐喻**（如左右对比、三齿轮、四象限等）。

## 标准化设计模板

### 通用结构

```
 第N章 · [标题]（左上角）
       左概念图 ──→ 右概念图（居中）
       (旧问题)  箭头  (新答案)
  标签线 · 作者（底部居中）
```

### 配色方案（雾霁蓝系）

```
Deep:   #3A4E66   Mid:    #48607C
Accent: #5B9BC8   Light:  #A8C8E0
Gold:   #C8B99B   Paper:  #F5F0E8
```

### 尺寸

- 输出尺寸：1600×900 px (16:9)
- 插入PDF后自动缩放，无需额外适配

## 批量生成脚本模式

1. 定义一个 `chapters` 列表（每章：num, title, left_emoji, right_emoji, left_text, right_text, color）
2. 用 f-string 生成标准化手绘风格HTML（含 frame + paper texture + 两个概念圆 + 章号）
3. 用 Playwright 逐一张截图（1600×900, `goto('file:///...')`, `wait_for_timeout(2000)`）
4. 用正则 `re.sub(f"^# 第{num}章 ", ...)` 插入 merged-manuscript.md
5. 构建PDF

## 插入手稿

使用正则匹配 `^# 第N章 `（行首），在其前插入：

```markdown
![第N章 插图](assets/ch{N:02d}-{title}.png)
```

**注意**：插图应在 merge-book 之后、press-typeset 之前插入。merge-book.py 每次覆盖生成 merged-manuscript.md，因此不要在其前做手动编辑。

## 封面QR码集成

1. 将网站QR码 PNG 复制到 `assets/website-qrcode.png` 和 `output/` 目录
2. 修改 `press-typeset.py` 中 `generate_cover_html()` 函数，在封面底部右侧添加 `.cover-qr` 元素
3. 在 CSS 中添加 `.cover-qr` 样式（绝对定位、bottom:30px、right:30px）
4. 构建PDF

## 踩坑记录

- ❌ 不要在 merged-manuscript.md 上做手动文本编辑后再跑 merge-book.py → merge-book 会覆盖式生成，丢失手动修改
- ✅ 插图应在 merge-book 之后、press-typeset 之前插入
- ❌ 第一次生成插图时只生成了3章就发现 merged-manuscript 被损坏 → 后续修复合稿时，先备份再操作
- ✅ 用 `re.sub()` 带 `flags=re.MULTILINE` 匹配 `^# 第N章` 比字符串 `replace()` 更可靠
- ✅ 插图文件放入 `assets/` 目录，在 merged-manuscript 中用相对路径引用（`assets/ch01-xxx.png`），press-typeset 会自动复制到 output 目录
