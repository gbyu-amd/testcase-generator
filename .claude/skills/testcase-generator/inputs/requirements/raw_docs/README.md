# 原始文档存放目录

本目录用于存放产品经理提供的原始需求文档（Word、PDF 等二进制格式），不直接参与测试用例生成。

## 使用流程

1. 将原始 Word 文件放入本目录
2. 按需选择转换方式：

```bash
# 转换整份文档，写入 inputs/requirements/current_prd.md（默认输出路径）
python scripts/convert_docx.py inputs/requirements/raw_docs/<文件名>.docx --overwrite

# 转换整份文档，指定自定义输出路径
python scripts/convert_docx.py inputs/requirements/raw_docs/<文件名>.docx --output inputs/requirements/<自定义名>.md --overwrite

# 仅提取指定章节并打印（AI 直接调用，无需写文件）
python scripts/convert_docx.py inputs/requirements/raw_docs/<文件名>.docx --section "<章节名>" --print
```

转换时图片全部忽略，文字和表格完整保留。

## 注意事项

- 本目录文件不会被脚本自动扫描，只作为原始存档
- UI 设计图不放在这里，按章节名放在 `inputs/ui_design/<章节名>/` 下
