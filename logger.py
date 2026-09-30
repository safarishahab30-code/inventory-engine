import logging

logging.basicConfig(
    filename='inventory.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def log_transaction(action, item_id, amount):
    logging.info(f"Action: {action}, Item ID: {item_id}, Amount: {amount}")
import csv

def export_low_stock(data, filename="low_stock.csv"):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Name', 'Stock'])  # Header
        for item in data:
            writer.writerow([item.id, item.name, item.stock])
