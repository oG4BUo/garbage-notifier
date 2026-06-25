import csv
from pathlib import Path

import cv2
import numpy as np
import easyocr


def normalize_text(text):
    replacements = {
        "フラ": "プラ",
        "ナラ": "プラ",
        "ブラ": "プラ",
        "ララ": "プラ",
        "ワラ": "プラ",
        "岳": "缶",
        "缶": "缶",
        "砕": "破砕",
        "破": "破砕",
        "紙布": "紙・布",
        "紙-布": "紙・布",
        "ひん": "びん",
        "ピん": "びん",
        "可": "可燃",
        "可撚": "可燃",
        "河燃": "可燃",
        "ット": "ペット",
        "ペツト": "ペット",
        "蛍": "蛍光管",
        "蛍光": "蛍光管",
        "蛍光菅": "蛍光管",
        "か": "雑がみ",
        "雑かみ": "雑がみ",
        "雑力み": "雑がみ",
        "雛かみ": "雑がみ",
        "雄がみ": "雑がみ",
        "雛がみ": "雑がみ",
        "雄かみ": "雑がみ",
        " がみ": "雑がみ",
        "がみ": "雑がみ",
    }

    return replacements.get(text, text)


base_dir = Path(__file__).parent
cells_dir = base_dir / "cells"
debug_dir = base_dir / "cell_debug"
debug_dir.mkdir(exist_ok=True)

reader = easyocr.Reader(["ja", "en"])
rows = []
year = 2026
month = 1

print("=== 日ごとのOCR結果 ===")

for day in range(1, 32):
    image_path = cells_dir / f"day_{day:02}.png"

    image_data = np.fromfile(image_path, dtype=np.uint8)
    image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

    if image is None:
        print(f"{day}日: 画像を読み込めませんでした")
        continue

    height, width = image.shape[:2]

    # 上の日付部分を避けて、下側だけOCRする
    garbage_area = image[int(height * 0.25):height, int(width * 0.08):int(width * 0.92)]

    ocr_image = cv2.resize(
        garbage_area,
        None,
        fx=5,
        fy=5,
        interpolation=cv2.INTER_CUBIC
    )

    debug_path = debug_dir / f"day_{day:02}_ocr_area.png"
    cv2.imencode(".png", ocr_image)[1].tofile(debug_path)

    results = reader.readtext(ocr_image, detail=1)

    texts = []

    for result in results:
        text = result[1]
        confidence = result[2]

        if confidence < 0.2:
            continue

        normalized = normalize_text(text)

        if normalized.isdigit():
            continue

        if normalized in ["", ":", "・", "一", "-", "ー"]:
            continue

        texts.append(normalized)

    if texts:
        print(f"{day}日: {texts}")

    for garbage_type in texts:
        rows.append({
            "date": f"{year}-{month:02}-{day:02}",
            "garbage_type": garbage_type,
            "note": ""
        })

output_path = base_dir / "ocr_result.csv"

with open(output_path, "w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=["date", "garbage_type", "note"])
    writer.writeheader()
    writer.writerows(rows)

print(f"OCR結果をCSVに保存しました: {output_path}")