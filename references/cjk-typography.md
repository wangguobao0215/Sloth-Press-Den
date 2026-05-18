# CJK 书籍排版：CSS 要点与坑

从 sloth-press-den 开发中的调试经验提炼，适用于用 Chrome 原生打印引擎 + Playwright 渲染中文书籍 PDF。

---

## 核心规则

### 1. 不要对 CJK 文本使用 `text-align: justify`

**问题：** 浏览器为达到两端对齐，会在中文字符之间插入额外间距，产生"字与字间隔太大"的效果。

**正确：** `text-align: left`。中文每个字已是全宽，不需要 justify。

### 2. 每个元素显式声明 font-size

**问题：** 依赖 CSS 继承链给元素定字号时，Chrome 打印引擎可能丢失继承，导致不同元素使用不同字号。

**正确：** 对 `p`、`li`、`ul`、`ol`、`blockquote`、`h1`-`h3`、`code`、`pre` 全部显式声明 `font-size` 和 `line-height`。

```css
.chapter-body p {
    font-size: 11pt;
    line-height: 1.75;
}
.chapter-body li {
    font-size: 11pt;
    line-height: 1.6;
}
```

### 3. 双层边距防御

**问题：** CSS `@page { margin-top: 22mm; }` 可能不被 Paged.js 或 Chrome 打印引擎正确应用，导致内容从页面 y=0 开始，而 @top-center 的页眉也在顶部渲染——重叠。

**正确：** 同时设置 CSS @page margins 和 Playwright `page.pdf(margin=...)`，两者一致，形成 fallback。

```python
page.pdf(
    margin={"top": "22mm", "bottom": "22mm", "left": "20mm", "right": "16mm"},
    prefer_css_page_size=True,
)
```

```css
@page {
    margin-top: 22mm;
    margin-bottom: 22mm;
    margin-left: 20mm;
    margin-right: 16mm;
}
```

### 4. 不要用 Paged.js 排版中文书

**问题：** Paged.js v0.4.3 对 @page margins 的支持不可靠，经常不应用边距。且内嵌 33KB polyfill 增加 PDF 体积。

**建议：** 直接使用 Chrome 原生打印引擎。@page margin boxes（@top-center、@bottom-center）Chrome 原生支持。只有 `string()`（动态 running headers）需要 Paged.js，可以用固定书名字眉替代。

### 5. Python f-string + CSS 花括号转义

在 Python f-string 中生成 CSS 时，所有 CSS `{}` 必须写成 `{{}}`：

```python
return f'''
html {{
    font-size: {body_size}pt;
}}
'''
```

漏掉双花括号会导致 Python 将 CSS 花括号内的内容解释为变量名（`NameError: name 'margin' is not defined`）。

### 6. 章节扉页避免使用 min-height

**问题：** `min-height: 70vh` 或 `min-height: 100vh` 在打印分页时可能导致内容重叠。

**正确：** 使用 `padding: 4em 0` 替代，确保扉页有固定间距而不是最小高度。

---

## Chrome 原生打印引擎能力对照

| 能力 | Chrome 原生 | Paged.js |
|------|------------|----------|
| @page margins | ✅ | ⚠️ v0.4.3 不可靠 |
| @bottom-center 页码 | ✅ `counter(page)` | ✅ |
| @top-center 静态文本 | ✅ `content: "书名"` | ✅ |
| @top-center 动态运行头 | ❌ `string()` 不支持 | ✅ |
| named pages (@page cover) | ✅ | ✅ |
| page-break-before/after | ✅ | ✅ |
| page-break-inside: avoid | ✅ | ✅ |
| target-counter | ✅ | ✅ |
| footnotes | ⚠️ 有限支持 | ✅ |
| 文件体积 | 不需要 | +33KB polyfill |

---

## 常见 bug 诊断流程

当 PDF 出现排版问题时，按以下顺序排查：

1. **是否有重叠？** → @page margins 是否生效 → 加 Playwright margin 双重保险
2. **字体大小不一？** → 元素是否都有显式 font-size → 逐一检查 p/li/h/pre/code
3. **字间距太大？** → 是否使用了 text-align: justify → 改为 left
4. **分页不对？** → page-break 规则是否正确 → 检查 break-before/after 的值
5. **页眉不见了？** → Chrome 不支持 string() 运行头 → 改为静态书名
6. **CSS 解析错误？** → Python f-string 花括号是否双写 → 检查 {{ 和 }}
