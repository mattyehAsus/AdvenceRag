# Proposal: Add Parser Unit Tests

## Why
目前專案支援多種文件解析器（Docling, Unstructured, PyMuPDF），但解析過程容易受到外部依賴版本或檔案格式細微差異的影響。建立單元測試能確保解析邏輯的穩定性，並在更新依賴時及時發現 Regression。

## What Changes
- 在 `tests/unit/` 目錄下新增 `test_parsers.py`。
- 測試針對 `advence_rag/parsers/` 下的各類解析器：
    - `SimpleParser`: 驗證基礎純文本處理。
    - `detect_best_parser`: 驗證根據檔案類型自動指派解析器的邏輯。
    - 各類專業解析器的 Mock 測試：確保它們正確呼叫底層庫並轉換為 `Document` 物件。

## Impact
- **Positive**: 確保文件導入流程的第一步（解析）是可靠的。
- **Scope**: 僅限於測試程式碼，不會影響現有的業務邏輯。
