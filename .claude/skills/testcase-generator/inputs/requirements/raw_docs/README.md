# 原始文档存放目录

本目录用于存放产品经理提供的原始需求文档（Word、PDF 等二进制格式）。Word 文档作为来源存档保留在本目录，正式生成测试用例前需先整份转换并覆盖写入 `inputs/requirements/current_prd.md`。

## 使用流程

1. 将原始 Word 文件放入本目录
2. 生成测试用例前，先转换整份文档并覆盖当前 PRD：

```bash
# 转换整份文档，写入 inputs/requirements/current_prd.md（默认输出路径）
python scripts/convert_docx.py inputs/requirements/raw_docs/<文件名>.docx --overwrite

# 转换整份文档，指定自定义输出路径
python scripts/convert_docx.py inputs/requirements/raw_docs/<文件名>.docx --output inputs/requirements/<自定义名>.md --overwrite
```

转换时图片全部忽略，文字和表格完整保留。

## 注意事项

- 本目录文件不会被脚本自动扫描，只作为原始存档
- 当用户要求根据某个 `.docx` 章节生成测试用例时，必须先覆盖写入 `inputs/requirements/current_prd.md`，再从 `current_prd.md` 提取章节内容；不要只用 `--section --print` 临时读取后生成
- UI 设计图不放在这里，按章节名放在 `inputs/ui_design/<章节名>/` 下
