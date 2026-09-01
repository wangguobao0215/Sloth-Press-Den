<p align="center">
  <img src="assets/sloth-avatar-round.png" width="120" />
</p>

<h1 align="center">Sloth-Press-Den — 深印 · 写书工坊</h1>

<p align="center">
  从规划到出版的完整写书流水线 — 写作引擎 × 排版引擎 × 审校引擎，一站式成书。
</p>

<p align="center">
  <img src="assets/qrcode.jpg" width="140" /><br/>
  扫码关注「树懒老K」公众号 · <em>慢一点，深一度。</em>
</p>

---

## 品名释义

**深印 · 写书工坊**（Sloth-Press-Den）— "深" 承品牌哲学"慢一点，深一度"；"印" 取出版印刷之意，亦指深度印记。"Press" 即出版印刷，"Den" 是工坊、小窝。树懒写书，不赶工，求深入——每一本都是匠书。

## 功能概览

- **5阶段写作引擎**：规划 → 研究 → 写作 → 审校 → 构建（基于 lovstudio 工作流）
- **出版级排版**：A5 书籍排版、雾霁蓝/经典出版等 5 套专业预设、CJK 排版最佳实践
- **封面/封底系统**：圆形头像 + 渐变背景 + 公众号二维码
- **多格式输出**：PDF（Chrome 原生 @page 分页）、HTML、ePub、MOBI、AZW3
- **知识附件**：自动生产表编号、图编号、交叉引用、PDF 书签、章首题记
- **自动审校**：术语一致性、引用规范、排版规则检查

## 快速开始

### 前置条件

```bash
pip install markdown pygments pyyaml playwright qrcode Pillow
playwright install chromium
# 可选（用于 PDF 书签注入）：
pip install PyMuPDF
```

### 使用方式

在 QoderWork 中安装本技能后，直接对话即可触发：

- "帮我写一本书"→ 启动 5 阶段写作流程
- "把这本书排版成 PDF"→ 启动排版引擎
- "审校一下书稿"→ 运行自动审校

## 版本

当前版本：**3.4.0**

详见 [CHANGELOG.md](CHANGELOG.md)

## 许可证

[MIT License](LICENSE)
