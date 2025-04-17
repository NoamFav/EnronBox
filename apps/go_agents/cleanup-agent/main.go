package main

import (
    "database/sql"
    "fmt"
    _ "github.com/mattn/go-sqlite3"
)

func main() {
    fmt.Println("🧹 Running cleanup agent...")
    db, _ := sql.Open("sqlite3", "/app/data/enron.db")
    defer db.Close()
    db.Exec(`DELETE FROM emails WHERE body IS NULL OR body = ""`)
    fmt.Println("✅ Cleanup complete.")
}
