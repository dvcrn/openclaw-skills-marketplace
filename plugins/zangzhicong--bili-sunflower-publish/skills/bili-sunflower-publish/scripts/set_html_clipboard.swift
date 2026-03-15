// set_html_clipboard.swift
// Usage: swift set_html_clipboard.swift <path-to-html-file>
// Sets both text/html and text/plain on the macOS system clipboard.

import AppKit
import Foundation

guard CommandLine.arguments.count > 1 else {
    fputs("Usage: swift \(CommandLine.arguments[0]) <html-file>\n", stderr)
    exit(1)
}

let path = CommandLine.arguments[1]
let html = try String(contentsOfFile: path, encoding: .utf8)
let htmlData = html.data(using: .utf8)!

let pb = NSPasteboard.general
pb.clearContents()
pb.setData(htmlData, forType: .html)

// Also set plain text fallback (strip tags)
let plain = html.replacingOccurrences(of: "<[^>]+>", with: "", options: .regularExpression)
pb.setString(plain, forType: .string)

print("OK: \(htmlData.count) bytes HTML set to clipboard")
