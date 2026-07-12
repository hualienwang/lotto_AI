
import csv
from pathlib import Path


def find_latest_prediction_csv(folder="D:\\"):
    # 依修改時間尋找 D:\ 底下最新的 prediction_history_*.csv。
    files = list(Path(folder).glob("prediction_history_*.csv"))
    if not files:
        raise FileNotFoundError(f"找不到 {folder}prediction_history_*.csv")
    return max(files, key=lambda path: path.stat().st_mtime)


def parse_prediction_numbers(text):
    # 新版 CSV 會是 01,12,24,25,35；舊版可能是 0112242535。
    value = text.strip()
    if not value:
        return []

    if "," in value:
        parts = value.split(",")
    else:
        parts = [value[index:index + 2] for index in range(0, len(value), 2)]

    numbers = []
    for part in parts:
        try:
            numbers.append(int(part.strip()))
        except ValueError:
            pass
    return numbers


def load_given_numbers_from_latest_csv(folder="D:\\"):
    latest_file = find_latest_prediction_csv(folder)
    given_numbers = []

    with latest_file.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            given_numbers.extend(parse_prediction_numbers(row.get("預測號碼", "")))

    return given_numbers, latest_file


def find_missing_numbers(given_numbers):
    # 排除重複值，並只保留 1-39 之間的有效號碼。
    existing_numbers = {
        num for num in given_numbers
        if 1 <= num <= 39
    }

    # 建立 1-39 的完整號碼集合。
    all_numbers = set(range(1, 40))

    # 找出未出現的號碼並排序。
    return sorted(all_numbers - existing_numbers)


given_numbers, latest_csv = load_given_numbers_from_latest_csv()
missing = find_missing_numbers(given_numbers)

print(f"讀取檔案：{latest_csv}")
print(f"CSV 中的預測號碼 len：{len(given_numbers)}")
print([f"{num:02d}" for num in given_numbers])
print(f"未出現的號碼 len：{len(missing)}")
print([f"{num:02d}" for num in missing])
