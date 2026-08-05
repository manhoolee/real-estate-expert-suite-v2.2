---
name: wechat-article-exporter
description: >-
  v2.1 微信资料入口。仅在用户提供微信公众号文章链接、要求抓取/保存/转换微信文章，或总控需要将微信文章归档为研究证据时触发；不因普通地产研究自动触发。
---

# 微信资料入口 v2.1

## 两种模式

1. **研究归档模式**：被总控调用时，默认输出 Markdown + JSON，保留标题、作者、发布日期、原链接和抓取日期，然后将事实、观点、引用和待核验项交回研究链，不中断主任务询问格式。
2. **独立导出模式**：用户明确要阅读或转换时，再询问需要 Markdown、HTML、文本、JSON 或 Excel；已有明确格式则直接执行。

执行前读取 [research-intake.md](references/research-intake.md)。

## 脚本

```bash
python scripts/fetch_article.py <url> [format] [output_dir]
python scripts/batch_fetch.py <urls_file> [formats_csv]
```

抓取失败时说明原因，不伪造正文、作者、阅读量、点赞或评论。HTML 可本地化样式和图片；研究归档必须保留原链接及抓取日期。

## 证据边界

微信文章通常为 `FACT-C` 或观点材料，不能替代法定规划、政府公告、登记成交、合同或内部经营数据。引用文章中的官方数字时，优先回溯原始发布机关。若文章与官方文件冲突，保留冲突记录并以原始权威来源为准。

只有仍需用户选择导出方式或补充链接时才给下一步菜单；完成研究归档后直接回到总控任务。
