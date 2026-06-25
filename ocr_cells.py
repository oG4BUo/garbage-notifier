from pathlib import Path

import cv2
import numpy as np


base_dir = Path(__file__).parent
image_path = base_dir / "january.png"

image_data = np.fromfile(image_path, dtype=np.uint8)
image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

if image is None:
    raise FileNotFoundError(f"画像を読み込めませんでした: {image_path}")

height, width = image.shape[:2]

print(f"画像サイズ: width={width}, height={height}")

# この値は画像に合わせて調整します
calendar_left = 0
calendar_top = 50
calendar_right = 339
calendar_bottom = 465

calendar_width = calendar_right - calendar_left
calendar_height = calendar_bottom - calendar_top

cell_width = calendar_width / 7
cell_height = calendar_height / 5

preview = image.copy()

for i in range(8):
    x = int(calendar_left + i * cell_width)
    cv2.line(preview, (x, calendar_top), (x, calendar_bottom), (0, 0, 255), 1)

for i in range(6):
    y = int(calendar_top + i * cell_height)
    cv2.line(preview, (calendar_left, y), (calendar_right, y), (0, 0, 255), 1)

preview_path = base_dir / "grid_preview.png"
cv2.imencode(".png", preview)[1].tofile(preview_path)

print(f"確認用画像を作成しました: {preview_path}")

output_dir = base_dir / "cells"
output_dir.mkdir(exist_ok=True)

start_weekday = 4
days_in_month = 31

for day in range(1, days_in_month + 1):
    index = start_weekday + day - 1

    row = index // 7
    col = index % 7

    x1 = int(calendar_left + col * cell_width)
    y1 = int(calendar_top + row * cell_height)
    x2 = int(calendar_left + (col + 1) * cell_width)
    y2 = int(calendar_top + (row + 1) * cell_height)

    cell_image = image[y1:y2, x1:x2]

    output_path = output_dir / f"day_{day:02}.png"
    cv2.imencode(".png", cell_image)[1].tofile(output_path)

    print(f"{day}日: row={row}, col={col}, saved={output_path}")