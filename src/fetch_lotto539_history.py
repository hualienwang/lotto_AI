import argparse
import json
import sqlite3
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

import requests

BASE_URL = "https://www.taiwanlottery.com/lotto/result/traditional"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "lotto-539.db"


def shift_month(day, month_delta):
    month_index = day.year * 12 + day.month - 1 + month_delta
    year = month_index // 12
    month = month_index % 12 + 1
    return f"{year:04d}-{month:02d}"


def build_default_url(today=None):
    today = today or date.today()
    start_month = shift_month(today, -2)
    end_month = shift_month(today, 0)
    return (
        f"{BASE_URL}?game=daily_cash&period="
        f"&start_month={start_month}&end_month={end_month}"
    )


DEFAULT_URL = build_default_url()


class TableTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables = []
        self._table = None
        self._row = None
        self._cell = None
        self._in_cell = False

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self._table = []
        elif tag == "tr" and self._table is not None:
            self._row = []
        elif tag in {"th", "td"} and self._row is not None:
            self._cell = []
            self._in_cell = True

    def handle_data(self, data):
        if self._in_cell and self._cell is not None:
            text = " ".join(data.split())
            if text:
                self._cell.append(text)

    def handle_endtag(self, tag):
        if tag in {"th", "td"} and self._in_cell:
            self._row.append(" ".join(self._cell).strip())
            self._cell = None
            self._in_cell = False
        elif tag == "tr" and self._row is not None:
            if any(self._row):
                self._table.append(self._row)
            self._row = None
        elif tag == "table" and self._table is not None:
            if self._table:
                self.tables.append(self._table)
            self._table = None


def fetch_html(url):
    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=60,
            verify=False,
        )
        response.raise_for_status()
        return response.text
    except requests.RequestException as exc:
        raise RuntimeError("抓取歷史資料失敗，請稍後再試。") from exc


def fetch_history_records(today=None):
    start_month = shift_month(today or date.today(), -2)
    end_month = shift_month(today or date.today(), 0)

    try:
        response = requests.get(
            "https://api.taiwanlottery.com/TLCAPIWeB/Lottery/Daily539Result",
            params={
                "period": "",
                "month": start_month,
                "endMonth": end_month,
                "pageNum": 1,
                "pageSize": 200,
            },
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=60,
            verify=False,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise RuntimeError("抓取歷史資料失敗，請稍後再試。") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError("抓取歷史資料格式錯誤，請稍後再試。") from exc

    if payload.get("rtCode") != 0:
        raise RuntimeError(payload.get("rtMsg") or "抓取歷史資料失敗，請稍後再試。")

    records = []
    for item in payload.get("content", {}).get("daily539Res", []):
        records.append(
            {
                "期別": str(item.get("period", "")),
                "開獎日": item.get("lotteryDate", "")[:10],
                "大小順序": " ".join(str(x) for x in item.get("drawNumberAppear", [])),
                "頭獎中獎注數": int(item.get("d539JackpotAssign", {}).get("winnerCount", 0)),
            }
        )

    if not records:
        raise RuntimeError("沒有解析到任何今彩539資料，請確認查詢條件是否正確。")

    return records


def parse_history(html):
    parser = TableTextParser()
    parser.feed(html)

    records = []
    tables = parser.tables
    for index in range(len(tables) - 2):
        info_table = tables[index]
        number_table = tables[index + 1]
        prize_table = tables[index + 2]

        data_row = next(
            (
                row
                for row in info_table
                if row and row[0].isdigit() and len(row[0]) == 9
            ),
            None,
        )
        size_row = next(
            (row for row in number_table if row and row[0] == "大小順序"), None
        )
        winners_row = next(
            (row for row in prize_table if row and row[0] == "中獎注數"), None
        )

        if not data_row or not size_row or not winners_row:
            continue

        records.append(
            {
                "期別": data_row[0],
                "開獎日": data_row[1],
                "大小順序": " ".join(size_row[1:6]),
                "頭獎中獎注數": int(winners_row[1].replace(",", "")),
            }
        )

    if not records:
        raise RuntimeError(
            "沒有解析到任何今彩539資料，請確認頁面格式或查詢網址是否改變。"
        )

    return records


def resolve_db_path(db_path):
    if not db_path:
        return DEFAULT_DB_PATH

    db_path = Path(db_path)
    if not db_path.is_absolute():
        db_path = PROJECT_ROOT / db_path
    return db_path


def save_history(db_path, records):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                "期別" TEXT PRIMARY KEY,
                "開獎日" TEXT NOT NULL,
                "大小順序" TEXT NOT NULL,
                "頭獎中獎注數" INTEGER NOT NULL
            )
            """)
        conn.execute(
            'CREATE INDEX IF NOT EXISTS idx_history_draw_date ON history ("開獎日")'
        )
        before_count = conn.total_changes
        conn.executemany(
            """
            INSERT OR IGNORE INTO history ("期別", "開獎日", "大小順序", "頭獎中獎注數")
            VALUES (:期別, :開獎日, :大小順序, :頭獎中獎注數)
            """,
            records,
        )
        return conn.total_changes - before_count


def main():
    parser = argparse.ArgumentParser(
        description="抓取台彩今彩539歷史資料並寫入 SQLite。"
    )
    parser.add_argument(
        "--url",
        default="",
        help="(選填) 台彩查詢網址。若留空則使用官方 API 取得歷史資料。",
    )
    parser.add_argument(
        "--db",
        default="",
        help="輸出的 SQLite 資料庫路徑，預設為 lotto-539.db",
    )
    args = parser.parse_args()

    if args.url:
        html = fetch_html(args.url)
        records = parse_history(html)
    else:
        records = fetch_history_records()

    db_path = resolve_db_path(args.db)
    inserted_count = save_history(db_path, records)

    print(
        f"抓取 {len(records)} 筆資料，新增 {inserted_count} 筆到 {db_path} 的 history 表。"
    )
    print(f"最新期別：{records[0]['期別']}，最早期別：{records[-1]['期別']}")


if __name__ == "__main__":
    main()
