# Chrome 原生打印引擎处理 CJK 书籍的要点

> 2026-05-17 实测总结 — 替代 Paged.js v0.4.3 后的经验

## 背景

Paged.js v0.4.3 在处理中文书籍时出现系统性 bug：每页上半部分字体重叠、字体大小不一。根本原因是 Paged.js 对 `@page` margins 的应用不可靠，导致 @top-center running headers 与正文在页面顶部重叠。

解决方案：去掉 Paged.js，直接使用 Chrome 原生 `@page + @media print` 引擎。

## Chrome 原生 @page 支持情况

| CSS 特性 | Chrome @print 支持 | 替代方案 |
|----------|-------------------|----------|
| `@page { size: A5; }` | ✅ | 配合 Playwright `prefer_css_page_size=True` |
| `@page { margin: 22mm; }` | ✅ | 同时设 Playwright `page.pdf(margin=...)` 双保险 |
| `@page @bottom-center { counter(page) }` | ✅ | 用于页码，Chrome完全支持 |
| `@page @top-center { content: "文本"; }` | ✅ 仅静态文本 | ❌ 不支持 `string()` 运行元素 |
| `@page named pages (cover, toc)` | ✅ | Named pages 正常工作 |
| `@page @top-center { content: none; }` | ✅ | 用于封面和扉页不显示页眉 |
| `page-break-before/after/inside` | ✅ | 标准 CSS 属性，Chrome 完全支持 |
| `target-counter()` | ⚠️ 有限 | 目录页码，Chrome部分支持 |
| `string-set: chapter-title` | ❌ | 不支持 running elements，页眉用静态书名 |
| Paged.js polyfill | ❌ 不再需要 | 避免 33KB JS 内联 |

## 关键修复

### 1. 边距双保险

不要只在 CSS 中设 `@page margin` 而 Playwright 用 0：

```python
page.pdf(
    margin={"top": "22mm", "bottom": "22mm", "left": "20mm", "right": "16mm"},
    prefer_css_page_size=True,
)
```

### 2. 显式字号声明

每个正文元素都必须有 `font-size` 和 `line-height`，不能依赖 CSS 继承链：

```css
.chapter-body p, .chapter-body li,
.chapter-body ul, .chapter-body ol,
.chapter-body blockquote {
    font-size: 11pt;
    line-height: 1.75;
}
.chapter-body h1, .chapter-body h2, .chapter-body h3 {
    line-height: 1.4;
}
```

### 3. CJK 文字对齐

```css
/* ❌ text-align: justify 拉伸中文字间距 */
text-align: left;    /* ✅ 中文书籍左对齐 */
```

### 4. 背景色

```css
/* ❌ html设背景色 + print_background=True = 每页底色块 */
html { background-color: ...; }     /* ❌ */
/* ✅ 只写在封面等特定元素 */
.cover-page { background: ...; }    /* ✅ */
```

### 5. 页面顶部间距

```css
/* ❌ min-height 不稳定 */
.chapter-opener { min-height: 70vh; }  /* ❌ */
.chapter-opener { padding: 4em 0; }    /* ✅ */
```

### 6. 章节数字 letter-spacing

```css
/* ❌ 0.3em 使"第五章"变成"第 五 章" */
letter-spacing: 0.3em;   /* ❌ */
letter-spacing: 0.08em;  /* ✅ */
```

### 7. QR 码图片

Chrome print 不渲染 inline data URI。必须用真实文件：

```python
# ❌ inline base64 在 Chrome print 中不显示
qr.save(buf, format="PNG")
img = f'<img src="data:image/png;base64,{b64}"/>'     # ❌

# ✅ 真实文件引用
qr.save("output/qrcode.png", format="PNG")
img = '<img src="qrcode.png"/>'                       # ✅
```

### 8. 渲染等待

```python
page.wait_for_timeout(8000)  # 5s 偶有不稳定，推荐 8s
```

### 9. Markdown 扩展

```python
# ❌ 有问题
'nl2br',      # 过多 <br>
'sane_lists', # 行为不稳定

# ✅ 稳定
'tables', 'fenced_code', 'toc', 'smarty',
'footnotes', 'codehilite'
```

### 10. CSS f-string 双括号

Python f-string 中 CSS 花括号必须用 `{{ }}` 转义，否则 `{ margin: 0; }` 被 Python 识别为变量引用报错 `NameError: name 'margin' is not defined`。

## 与 Paged.js 方案对比

| 维度 | Paged.js v0.4.3 | Chrome 原生 @print |
|------|----------------|-------------------|
| 渲染可靠性 | ❌ @page margin 不应用导致重叠 | ✅ 稳定 |
| 文件大小 | 2.3MB（内嵌33KB JS） | 1.9MB |
| running headers | ✅ string() 动态章节标题 | ❌ 只支持静态文本 |
| 依赖 | JS polyfill 33,251行 | 无额外依赖 |
| 中文排版稳定性 | ❌ 多次发现 CJK bug | ✅ Chrome 打印引擎成熟 |
