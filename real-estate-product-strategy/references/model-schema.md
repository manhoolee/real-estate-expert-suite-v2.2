# product_model.py 输入结构

```json
{
  "project": "示例项目",
  "scope_id": "phase-1-residential",
  "residential_gfa_sqm": 222740,
  "saleable_ratio": 0.92,
  "segments": [
    {
      "name": "改善",
      "share": 0.6,
      "avg_unit_gfa": 140,
      "prices": {"conservative": 110000, "base": 120000, "optimistic": 130000}
    }
  ],
  "total_cost_yuan": null
}
```

规则：`share` 合计为 1；面积为平方米；价格为元/平方米；成本为总额人民币元。`saleable_ratio` 与价格属于模型假设时必须在报告标为 `HYPOTHESIS`。脚本输出不代表市场或财务事实。
