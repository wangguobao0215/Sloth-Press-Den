# 外部工具调研 — 出版排版生态（2026-05-17）

## Paged.js
- 事实标准：CSS Paged Media polyfill
- BookSmith-Den 内核
- 优势：CSS控制一切排版
- 官网：pagedjs.org

## Typst
- 新兴排版系统，Rust编写
- 比LaTeX更现代，比CSS更精确
- CJK支持在发展中
- 值得关注

## Quarto
- 多格式科学出版（R Markdown继承者）
- 输出：PDF/HTML/Word/ePub/幻灯片
- 强在学术出版，弱在企业白皮书

## Pandoc
- 通用文档转换器
- BookSmith-Den 已弃用

## Prince XML
- 商业CSS分页渲染器
- 最专业的CSS打印渲染
- 收费

## WeasyPrint
- 开源CSS分页渲染
- 比Playwright更轻量
- CJK支持一般

## 结论

BookSmith-Den 选择 Playwright + Paged.js 是正确方向：
- 开源免费
- 全CSS控制
- 浏览器渲染 = 所见即所得
- 生态活跃

Typst 值得持续关注，等CJK支持成熟后可考虑。
