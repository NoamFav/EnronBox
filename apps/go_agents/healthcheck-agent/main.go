package main

import (
    "database/sql"
    "fmt"
    _ "github.com/mattn/go-sqlite3"
)

func main() {
    fmt.Println("🩺 Performing health check...")
    db, _ := sql.Open("sqlite3", "/app/data/enron.db")
    defer db.Close()
    var result string
    db.QueryRow(`PRAGMA integrity_check`).Scan(&result)
    fmt.Println("Health Check:", result)
}
