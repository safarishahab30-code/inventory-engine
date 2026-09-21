import csv
from pathlib import Path
from typing import List, Dict, Any
from openpyxl import Workbook

def export_to_csv(data: List[Dict[str, Any]], file_path: Path) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if not data:
        return
    with open(file_path, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
        writer.writeheader()
        writer.writerows(data)

def export_to_excel(data: List[Dict[str, Any]], file_path: Path) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.title = "Inventory Report"
    if data:
        ws.append(list(data[0].keys()))
        for row in data:
            ws.append(list(row.values()))
    wb.save(file_path)
