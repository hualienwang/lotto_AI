# 今彩539 開獎記錄 / 預測系統

這個專案是一個 Flask 應用程式，提供今彩 539 的歷史資料查詢、手動錄入、歷史抓取與預測頁面。

## 目前狀態

- 後端：Flask 3.0.0
- 生產伺服器：Gunicorn 21.2.0
- 資料來源：台彩官方 JSON API（不再依賴 Playwright / 瀏覽器）
- 資料庫：SQLite
- 部署平台：Vercel（Python runtime）

## 功能

- 📊 查看歷史開獎紀錄
- 🔄 抓取最新今彩539歷史資料（官方 API）
- ✏️ 手動新增/覆蓋歷史紀錄
- 🔮 預測頁面與模型入口
- 📤 匯出 CSV

## 目錄結構

```text
.
├── app.py                  # Flask 入口
├── requirements.txt        # Python 相依套件
├── vercel.json             # Vercel 部署設定
├── src/
│   ├── database.py         # SQLite 連線與資料庫路徑
│   ├── fetch_lotto539_history.py  # 抓取歷史資料
│   ├── predictor.py        # 預測邏輯
│   ├── routes.py           # API 與頁面路由
│   └── utils.py
└── templates/              # HTML 頁面
```

## 本地開發

### 1. 建立環境

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 啟動應用

```bash
python app.py
```

開啟：

```text
http://127.0.0.1:5000/
```

## API 端點

### 歷史資料

```http
GET /api/history?limit=10&start=115000001&end=115000200
```

### 手動新增紀錄

```http
POST /api/manual
Content-Type: application/json
```

範例：

```json
{
  "period": "115000141",
  "numbers": "39,32,35,1,4",
  "draw_date": "2026-06-10"
}
```

### 抓取歷史資料

```http
POST /api/fetch-history
```

此路由會直接呼叫官方台彩 JSON API，並寫入 SQLite。

### 下一期期數

```http
GET /api/next-period
```

### 預測

```http
GET /api/predict?type=ai
```

### 匯出 CSV

```http
POST /api/export-csv
Content-Type: application/json
```

## Vercel 部署

### 1. 安裝 Vercel CLI

```bash
npm install -g vercel
```

### 2. 部署

```bash
vercel login
vercel --prod
```

### 3. 資料庫寫入注意事項

Vercel 是 serverless 環境，檔案系統通常是暫時且可能是唯讀的。

目前程式已改為：

- 預設使用系統暫存資料夾中的 SQLite 檔案：`/tmp/lotto-539.db`
- 若需要指定位置，可設定環境變數：

```bash
LOTTO_DB_PATH=/tmp/lotto-539.db
```

> 如果你要在 Vercel 上保留長期資料，建議改用外部資料庫（例如 Neon / Supabase / Vercel Postgres）。

## 重要變更說明

這個版本已移除歷史抓取流程中對 Playwright / 瀏覽器安裝的依賴，改為直接使用官方資料 API，避免 Vercel 部署時因瀏覽器執行環境失敗。

## 常見問題

### 1. 為什麼抓取歷史資料不再用 Playwright？

因為 Vercel 的執行環境不適合依賴瀏覽器安裝與 headless browser。官方 API 可直接取得歷史資料，速度更穩定也更適合部署。

### 2. Vercel 上資料會不會持久保存？

不保證。serverless 環境的檔案可能會在重新啟動或部署後消失。若需要長期保存資料，請使用外部資料庫。

## 授權

MIT
