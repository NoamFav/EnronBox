package main

import (
    "database/sql"
    "fmt"
    _ "github.com/mattn/go-sqlite3"
)

func main() {
    fmt.Println("📊 Running ANALYZE...")
    db, _ := sql.Open("sqlite3", "/app/data/enron.db")
    defer db.Close()
    db.Exec(`ANALYZE`)
    fmt.Println("✅ ANALYZE complete.")
}
