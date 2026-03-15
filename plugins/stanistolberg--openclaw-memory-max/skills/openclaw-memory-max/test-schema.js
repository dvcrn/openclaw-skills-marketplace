const db = require("/home/claw/.openclaw/extensions/openclaw-memory-max/node_modules/better-sqlite3")("/home/claw/.openclaw/memory/main.sqlite");
console.log("Columns in chunks:", db.prepare("PRAGMA table_info(chunks)").all());
console.log("Columns in files:", db.prepare("PRAGMA table_info(files)").all());
