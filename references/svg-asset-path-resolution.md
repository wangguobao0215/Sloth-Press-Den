# SVG 图片资产路径修复实录

## 问题现象

PDF 中的对比图、泳道图显示为空白（SVG 图片不渲染）。

## 根因

`press-typeset.py` 将 Markdown 转为 HTML 后写入 `output/_temp_book.html`。HTML 中图片引用保持原相对路径 `assets/ch02-l1-compare.svg`。

浏览器解析这个路径时，是相对于 HTML 文件位置（`output/`）的，所以它找的是 `output/assets/ch02-l1-compare.svg`——而这个目录不存在。

SVG 实际位置：`<项目根>/assets/ch02-l1-compare.svg`

## 诊断步骤

1. 确认 PDF 有 75+ 个 XObject（图片对象）——说明浏览器尝试渲染了图片但可能是空白
2. 检查 `output/assets/` 是否存在——不存在则根因确认
3. 检查 `_temp_book.html` 中 `<img src="...">` 路径——确认是相对路径

## 修复

构建前将 SVG 资产复制到 output：

```bash
mkdir -p output/assets
cp assets/ch0*.svg output/assets/ 2>/dev/null
cp assets/*.png output/assets/ 2>/dev/null
```

## 永久修复

在 `build-pdf.sh` 中加入上述复制步骤。

## 注意事项

- `_ensure_asset()` 函数处理了封面头像和QR码，但书稿正文中 `![]()` 引用的图片需手动复制
- PNG 图片同理——只要 HTML 和图片不在同一目录，相对路径就断裂
- 所有书稿的图片都放在 `assets/` 目录下，构建脚本必须确保复制到 `output/assets/`
