# 原始文档存放目录

本目录用于存放产品经理提供的原始需求文档。Word `.docx` 文档作为默认可提取事实源，正式生成测试用例时直接从 `.docx` 提取指定章节；PDF 等其他格式仅作归档，如需使用应先转为 `.docx` 或由用户提供文本内容。

## 使用流程

1. 将原始 Word 文件放入本目录。
2. 生成测试用例时，优先直接提取指定章节：

```bash
# 列出章节
python scripts/extract_docx.py inputs/requirements/raw_docs/<文件名>.docx --list-sections

# 直接提取指定章节，供 Agent 生成用例
python scripts/extract_docx.py inputs/requirements/raw_docs/<文件名>.docx --section "<章节名>" --print
```

提取时图片全部忽略，文字和表格尽量保留为可读文本。

## 注意事项

- 本目录文件不会被脚本自动扫描，只作为原始存档和 Word 事实源
- 当用户要求根据某个 `.docx` 章节生成测试用例时，默认直接使用 `--section --print` 提取章节内容
- UI 设计图不放在这里，按章节名放在 `inputs/ui_design/<章节名>/` 下
