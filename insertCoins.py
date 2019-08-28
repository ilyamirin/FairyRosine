import sqlite3
import json
import random
import html

with open("json.json") as f:
    data = json.loads(f.read())

conn = sqlite3.connect('db.sqlite3')

c = conn.cursor()

def get_value_from_row_by_key(row, key):
    if key not in row.keys():
        return ""
    return html.unescape(row[key])

for row in data:
    imgs = row["imgs"]
    fields = [
        random.randint(6, 10),
        get_value_from_row_by_key(row, "name"),
        get_value_from_row_by_key(row, "short_name"),
        get_value_from_row_by_key(row, "nominal"),
        get_value_from_row_by_key(row, "quality"),
        get_value_from_row_by_key(row, "probe"),
        get_value_from_row_by_key(row, "original_equipment"),
        get_value_from_row_by_key(row, "pure_metal"),
        get_value_from_row_by_key(row, "mass"),
        get_value_from_row_by_key(row, "diameter"),
        get_value_from_row_by_key(row, "thickness"),
        get_value_from_row_by_key(row, "copies"),
        get_value_from_row_by_key(row, "manufacturer"),
        get_value_from_row_by_key(row, "notes"),
        get_value_from_row_by_key(row, "description"),
    ]

    imgs = [s.replace('"', '') for s in imgs]

    c.execute("INSERT INTO coinCatalog_coin (category_id, lang, name, short_name, nominal, quality, probe, original_equipment, pure_metal, mass, diameter, thickness, copies, manufacturer, notes, description) VALUES (?, 'en', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", fields)

    lastid = c.lastrowid

    for s in imgs:
        c.execute("INSERT INTO coinCatalog_imgcoin (coin_id, href) VALUES (?, ?)", [lastid, s])

    conn.commit()

conn.close()
