package main

import (
    "database/sql"
    "fmt"
    _ "github.com/mattn/go-sqlite3"
)

func main() {
    fmt.Println("🗜️  Vacuuming database...")
    db, _ := sql.Open("sqlite3", "/app/data/enron.db")
    defer db.Close()
    db.Exec(`VACUUM`)
    fmt.Println("✅ Vacuum complete.")
}
