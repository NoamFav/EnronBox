package main

import (
    "database/sql"
    "fmt"
    _ "github.com/mattn/go-sqlite3"
)

func main() {
    fmt.Println("🔁 Running migration agent...")
    db, _ := sql.Open("sqlite3", "/app/data/enron.db")
    defer db.Close()
    db.Exec(`ALTER TABLE emails ADD COLUMN word_count INTEGER`)
    fmt.Println("✅ Column added. Populate logic TBD.")
}
