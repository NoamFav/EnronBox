package main

import (
    "database/sql"
    "fmt"
    _ "github.com/mattn/go-sqlite3"
)

func main() {
    fmt.Println("🏗️  Creating indexes...")
    db, _ := sql.Open("sqlite3", "/app/data/enron.db")
    defer db.Close()
    db.Exec(`CREATE INDEX IF NOT EXISTS idx_user_id ON emails(user)`)
    db.Exec(`CREATE INDEX IF NOT EXISTS idx_folder ON emails(folder)`)
    fmt.Println("✅ Indexes created.")
}
