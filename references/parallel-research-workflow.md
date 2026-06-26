# Parallel Research Workflow for Technical Books

> Phase 2 实操：如何用并行搜索快速完成研究

## 核心策略

不要串行搜索。用 `delegate_task` 同时跑3条独立线，汇总到 `references/` 目录。

## 三条搜索线

### 线A: 学术论文

**工具**: arXiv API + Semantic Scholar API  
**搜索方法**: 用 `scripts/search_arxiv.py` 或直接curl Semantic Scholar  
**关键词策略**: 
- 对制造业主数据/本体类话题，arXiv噪声极大（Gene Ontology霸榜）
- 优先用排除词: `manufacturing ontology NOT gene`
- 或限分类: `cat:cs.AI OR cat:cs.DB OR cat:cs.SE`
- Semantic Scholar 的搜索排序更精准，优先使用

**产出**: 6-10篇高相关论文，每篇标注arXiv ID、标题、年份、摘要(200字)、相关度(高/中/低)

### 线B: 工业实践

**工具**: web_search + Jina Reader (via curl)  
**搜索方法**: 中英文混合搜索
- 英文: "manufacturing ontology ERP semantic" / "OPC UA ontology manufacturing" / "knowledge graph production"
- 中文: "制造业主数据 本体" / "语义集成 制造业 ERP" / "数据编织 制造业"

**目标**: 抓有具体企业名称和项目描述的案例
**产出**: 10-20个工业案例，含企业名称、来源、摘要、相关度评级

### 线C: 开源工具

**工具**: gh CLI + GitHub REST API  
**搜索方法**: 按主题搜索GitHub仓库
- "manufacturing ontology" / "BOM ontology" / "semantic middleware manufacturing"
- 检查stars、活跃度、文档完整性

**产出**: 8-15个开源项目，含仓库名、描述、stars、相关度

## 汇总存储

```
references/core-papers.md      — 论文摘要+引用
references/industry-cases.md   — 企业案例汇总
references/open-source-tools.md — 开源项目清单
```

## 翻车记录

- ❌ delegate_task的学术论文搜索线容易超时(arXiv API慢) → 先跑工业实践+工具线,再专门补学术线
- ❌ "manufacturing ontology"在arXiv=基因本体论淹没 → 必须加排除词或走Semantic Scholar  
- ❌ Semantic Scholar API不稳定(SSL handshake timeout) → 加重试逻辑,超时就走arXiv手动搜
- ❌ 不要在一轮delegate_task中放超过3个任务 → 每个任务有600s超时,太多并行互相拖累
