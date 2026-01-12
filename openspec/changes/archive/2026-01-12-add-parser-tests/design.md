# Design: Parser Unit Tests

## Test Scenarios
1. **Parser Selection**:
    - `detect_best_parser("test.pdf")` -> `ParserType.DOCLING` (or designated default).
    - `detect_best_parser("test.txt")` -> `ParserType.SIMPLE`.
2. **SimpleParser**:
    - 傳入純文字檔案，驗證輸出的 `Document` 物件包含正確的 `content` 與基礎 `metadata`。
3. **Mocked Professional Parsers**:
    - 由於環境中不一定安裝了所有底層庫（如 Docling），我們將使用 `unittest.mock` 來模擬底層解析邏輯。
    - 驗證 `DoclingParser.parse()` 是否正確封裝了 `docling` 的轉換流程。

## Test Data
- 建立一組小型測試檔案於 `tests/assets/`：
    - `sample.txt`
    - `dummy.pdf` (0-byte 或 極簡 PDF)

## Fixtures
- 在 `conftest.py` 中新增 `test_assets_dir` fixture。
