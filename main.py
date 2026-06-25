import json
import sqlite3
import sys
from pathlib import Path
from datetime import date, timedelta

import pandas as pd
from plyer import notification

def load_config(file_name):
    base_dir = Path(__file__).parent
    file_path = base_dir / file_name

    if not file_path.exists():
        raise FileNotFoundError(
            f"{file_name} が見つかりません。main.py と同じフォルダに置いてください。"
        )

    with open(file_path, "r", encoding="utf-8") as file:
        config = json.load(file)

    if "schedule_file" not in config:
        raise ValueError("config.json に schedule_file がありません。")

    if "notify_tomorrow" not in config:
        raise ValueError("config.json に notify_tomorrow がありません。")

    return config

def load_schedule(file_name):
    base_dir = Path(__file__).parent
    file_path = base_dir / file_name

    if not file_path.exists():
        raise FileNotFoundError(
            f"{file_name} が見つかりません。config.json の schedule_file を確認してください。"
        )

    if file_path.suffix == ".csv":
        df = pd.read_csv(file_path)
    elif file_path.suffix == ".xlsx":
        df = pd.read_excel(file_path)
    else:
        raise ValueError("対応している予定表ファイルは .csv または .xlsx です。")

    required_columns = ["date", "garbage_type", "note"]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"予定表に {column} 列がありません。")

    try:
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    except Exception:
        raise ValueError("date列の日付形式を確認してください。例: 2026-01-07")

    return df

def get_database_path():
    base_dir = Path(__file__).parent
    return base_dir / "garbage.db"


def create_database():
    db_path = get_database_path()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS garbage_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            garbage_type TEXT NOT NULL,
            note TEXT,
            UNIQUE(date, garbage_type)
        )
    """)

    conn.commit()
    conn.close()

def save_to_database(df):
    db_path = get_database_path()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for _, row in df.iterrows():
        note = row["note"]

        if pd.isna(note):
            note = ""

        cursor.execute("""
            INSERT INTO garbage_schedule (date, garbage_type, note)
            VALUES (?, ?, ?)
            ON CONFLICT(date, garbage_type)
            DO UPDATE SET note = excluded.note
        """, (row["date"], row["garbage_type"], note))

    conn.commit()
    conn.close()

def find_garbage_from_database(target_date):
    db_path = get_database_path()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    target_date_text = str(target_date)

    cursor.execute("""
        SELECT date, garbage_type, note
        FROM garbage_schedule
        WHERE date = ?
    """, (target_date_text,))

    rows = cursor.fetchall()

    conn.close()

    return rows


def show_garbage_rows(title, rows):
    print(f"=== {title} ===")

    if not rows:
        print("収集予定がありません。")
    else:
        for row in rows:
            print(f"ごみの種類: {row[1]}")

            if row[2]:
                print(f"メモ: {row[2]}")

def notify_tomorrow_garbage_rows(rows, target_date):
    if not rows:
        return

    garbage_list = []

    for row in rows:
        garbage_list.append(row[1])

    date_text = f"{target_date.month}月{target_date.day}日"
    message = "、".join(garbage_list)

    notification.notify(
        title=f"明日 {date_text} のごみ",
        message=message,
        timeout=10
    )

def show_all_database_rows():
    db_path = get_database_path()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, date, garbage_type, note
        FROM garbage_schedule
        ORDER BY date
    """)

    rows = cursor.fetchall()

    conn.close()

    print("=== データベースの中身 ===")

    for row in rows:
        print(row)

def import_schedule():
    config = load_config("config.json")

    df = load_schedule(config["schedule_file"])

    create_database()
    clear_database()
    save_to_database(df)

    print("予定表をデータベースに取り込みました。")

def notify_schedule():
    config = load_config("config.json")

    create_database()

    today = date.today()
    tomorrow = today + timedelta(days=1)

    today_rows = find_garbage_from_database(today)
    tomorrow_rows = find_garbage_from_database(tomorrow)

    today_title = f"今日 {today.month}月{today.day}日のごみ"
    tomorrow_title = f"明日 {tomorrow.month}月{tomorrow.day}日のごみ"

    show_garbage_rows(today_title, today_rows)
    print()
    show_garbage_rows(tomorrow_title, tomorrow_rows)

    if config["notify_tomorrow"]:
        notify_tomorrow_garbage_rows(tomorrow_rows, tomorrow)

def clear_database():
    db_path = get_database_path()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM garbage_schedule")

    conn.commit()
    conn.close()

def main():
    try:
        if len(sys.argv) < 2:
            print("使い方: python main.py import または python main.py notify")
            return

        command = sys.argv[1]

        if command == "import":
            import_schedule()
        elif command == "notify":
            notify_schedule()
        elif command == "show":
            show_all_database_rows()
        else:
            print("使えるコマンドは import、notify、show です。")

    except Exception as error:
        print("エラーが発生しました。")
        print(error)

if __name__ == "__main__":
    main()