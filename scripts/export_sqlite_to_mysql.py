import sqlite3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'data' / 'catchhot.db'
OUT_SCHEMA = ROOT / 'mysql_schema.sql'
OUT_INSERTS = ROOT / 'mysql_inserts.sql'

if not DB.exists():
    print('ERROR: sqlite DB not found at', DB)
    raise SystemExit(1)

con = sqlite3.connect(str(DB))
con.row_factory = sqlite3.Row
cur = con.cursor()

# Hard-coded CREATE TABLE statements matching models.py
schema_sql = '''-- MySQL schema generated from SQLite data

CREATE DATABASE IF NOT EXISTS `catchhot` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `catchhot`;

CREATE TABLE IF NOT EXISTS `tags` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `keyword` VARCHAR(200) NOT NULL,
  `keywords` JSON DEFAULT NULL,
  `platforms` JSON DEFAULT NULL,
  `interval_minutes` INT NOT NULL DEFAULT 60,
  `enabled` TINYINT(1) NOT NULL DEFAULT 1,
  `deleted` TINYINT(1) NOT NULL DEFAULT 0,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `jobs` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `tag_id` INT NOT NULL,
  `platform` VARCHAR(50) NOT NULL,
  `status` VARCHAR(20) NOT NULL,
  `retry_count` INT NOT NULL DEFAULT 0,
  `items_fetched` INT NOT NULL DEFAULT 0,
  `items_saved` INT NOT NULL DEFAULT 0,
  `error_message` TEXT,
  `started_at` DATETIME NOT NULL,
  `finished_at` DATETIME DEFAULT NULL,
  FOREIGN KEY (`tag_id`) REFERENCES `tags`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `hot_items` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `tag_id` INT NOT NULL,
  `platform` VARCHAR(50) NOT NULL,
  `title` VARCHAR(500) NOT NULL,
  `url` TEXT NOT NULL,
  `summary` TEXT DEFAULT NULL,
  `published_at` DATETIME DEFAULT NULL,
  `hot_score` DOUBLE NOT NULL DEFAULT 0.0,
  `score` DOUBLE NOT NULL DEFAULT 0.0,
  `meta` JSON DEFAULT NULL,
  `fingerprint` VARCHAR(64) NOT NULL,
  `fetched_at` DATETIME NOT NULL,
  FOREIGN KEY (`tag_id`) REFERENCES `tags`(`id`) ON DELETE CASCADE,
  UNIQUE KEY `uq_tag_fingerprint` (`tag_id`,`fingerprint`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
'''

with open(OUT_SCHEMA, 'w', encoding='utf-8') as f:
    f.write(schema_sql)
print('Wrote schema to', OUT_SCHEMA)

# helper to escape SQL literals
def sql_literal(val):
    if val is None:
        return 'NULL'
    if isinstance(val, str) and val.strip().lower() == 'null':
        return 'NULL'
    if isinstance(val, (int,)) and not isinstance(val, bool):
        return str(val)
    if isinstance(val, float):
        return repr(val)
    if isinstance(val, bool):
        return '1' if val else '0'
    # try to detect JSON stored as text
    try:
        if isinstance(val, str):
            # strip surrounding whitespace
            s = val.strip()
            # if seems like JSON
            if (s.startswith('{') and s.endswith('}')) or (s.startswith('[') and s.endswith(']')):
                # validate
                try:
                    json.loads(s)
                    body = s.replace("'", "\\'")
                    return "'{}'".format(body)
                except Exception:
                    pass
            # fallback: escape single quotes
            return "'{}'".format(val.replace("'", "''"))
    except Exception:
        pass
    # fallback stringify
    return "'{}'".format(str(val).replace("'", "''"))

# tables to export
tables = ['tags', 'jobs', 'hot_items']

with open(OUT_INSERTS, 'w', encoding='utf-8') as out:
    out.write('-- INSERT statements generated from SQLite\n')
    out.write('USE `catchhot`;\n')
    out.write('SET FOREIGN_KEY_CHECKS=0;\n')
    for t in tables:
        # get columns
        cur.execute(f"PRAGMA table_info('{t}')")
        cols_info = cur.fetchall()
        cols = [row['name'] for row in cols_info]
        if not cols:
            print('Table', t, 'does not exist or has no columns, skipping')
            continue
        rows = cur.execute(f"SELECT * FROM {t}").fetchall()
        print(f"Exporting {len(rows)} rows from {t}")
        for r in rows:
            values = []
            for c in cols:
                val = r[c]
                # sqlite may store booleans as 0/1 ints
                values.append(sql_literal(val))
            stmt = f"INSERT INTO `{t}` ({', '.join(['`'+c+'`' for c in cols])}) VALUES ({', '.join(values)});\n"
            out.write(stmt)
    out.write('SET FOREIGN_KEY_CHECKS=1;\n')
    for t in tables:
        max_id = cur.execute(f"SELECT COALESCE(MAX(id), 0) FROM {t}").fetchone()[0]
        if max_id:
            out.write(f"ALTER TABLE `{t}` AUTO_INCREMENT = {max_id + 1};\n")

print('Wrote inserts to', OUT_INSERTS)
con.close()
