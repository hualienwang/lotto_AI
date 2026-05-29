# 今彩539開獎預測系統

一個基於 Flask 的彩票開獎記錄管理與預測系統。

## 功能特性

- 📊 **歷次開獎記錄** - 查詢並管理彩票開獎歷史
- 🔮 **預測開獎** - 基於歷史數據的開獎預測
- ✏️ **手動輸入** - 支持手動新增開獎記錄
- 📥 **導出功能** - 將預測記錄導出為 CSV 格式

## 技術棧

- **後端框架**: Flask 3.0
- **數據庫**: SQLite
- **生產伺服器**: Gunicorn
- **前端**: HTML + JavaScript

## 本地運行

### 前置要求

- Python 3.9+
- pip

### 安裝依賴

```bash
pip install -r requirements.txt
```

### 啟動應用

開發模式：
```bash
python app.py
```

應用將運行在 `http://localhost:5000`

## 部署到 Render.com

### 前置條件

1. 在 [render.com](https://render.com) 上註冊帳號
2. 將項目推送至 GitHub

### 部署步驟

1. 登入 Render.com 控制台
2. 選擇 **New +** > **Web Service**
3. 連接您的 GitHub 倉庫
4. 配置如下：
   - **Name**: lotto-ai
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --workers 4 --worker-class sync --bind 0.0.0.0:$PORT app:app`
5. 點擊 **Create Web Service** 進行部署

### 或使用 render.yaml 部署

本項目已包含 `render.yaml` 配置文件，Render.com 會自動讀取此文件進行部署。

## API 端點

### 歷史記錄

```
GET /api/history?limit=10&start=001&end=100
```

查詢彩票開獎記錄。

**參數：**
- `limit` (可選): 返回記錄數量
- `start` (可選): 期數範圍開始
- `end` (可選): 期數範圍結束

### 新增記錄

```
POST /api/manual
Content-Type: application/json

{
  "period": "001",
  "numbers": "12,34,56,78,90",
  "draw_date": "2026-01-01"
}
```

### 下一期期數

```
GET /api/next-period
```

### 導出 CSV

```
POST /api/export-csv
Content-Type: application/json

{
  "csvContent": "..."
}
```

## 文件結構

```
lotto_AI/
├── app.py                 # Flask 主應用程序
├── lotto-539.db          # SQLite 數據庫
├── history.html          # 歷次開獎記錄頁面
├── predict.html          # 預測開獎頁面
├── manual.html           # 手動輸入頁面
├── requirements.txt      # Python 依賴列表
├── render.yaml           # Render.com 部署配置
└── README.md             # 項目文檔
```

## 常見問題

### 數據持久化

Render.com 的應用實例使用臨時文件系統。SQLite 數據庫文件可能會在應用重啟時丟失。建議遷移至：
- PostgreSQL（Render 原生支持）
- 雲存儲服務（如 AWS S3）

### 環境變量

如需添加環境變量，在 Render.com 控制台的 **Environment** 選項卡中設置。

## 許可證

MIT

## 聯絡方式

如有問題或建議，歡迎提交 Issue 或 Pull Request。
