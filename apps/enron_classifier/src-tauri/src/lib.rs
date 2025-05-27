use std::process::{Command, Stdio};
use tauri::path::BaseDirectory;
use tauri::Manager;

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![greet])
        .setup(|app| {
            let resource_path = app
                .path()
                .resolve("bin/flask-backend", BaseDirectory::Resource)
                .expect("Failed to resolve resource path");

            Command::new(resource_path)
                .stdout(Stdio::null())
                .stderr(Stdio::null())
                .spawn()
                .expect("Failed to launch Flask backend");

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
