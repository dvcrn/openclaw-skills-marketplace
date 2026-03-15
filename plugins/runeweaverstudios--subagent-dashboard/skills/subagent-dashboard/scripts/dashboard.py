#!/usr/bin/env python3
"""
Subagent Dashboard - Web UI for monitoring OpenClaw subagents.

Provides real-time monitoring, transcript viewing, and agent management.
"""

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS

# OpenClaw paths
OPENCLAW_HOME = Path(os.environ.get("OPENCLAW_HOME", str(Path.home() / ".openclaw")))
WORKSPACE_PATH = Path(os.environ.get("OPENCLAW_WORKSPACE", str(OPENCLAW_HOME / "workspace")))
PROJECT_LABEL = WORKSPACE_PATH.name or "workspace"
TRACKER_SCRIPT = OPENCLAW_HOME / "workspace" / "skills" / "subagent-tracker" / "scripts" / "subagent_tracker.py"
SESSIONS_PATH = OPENCLAW_HOME / "agents" / "main" / "sessions"
SESSIONS_JSON = SESSIONS_PATH / "sessions.json"
RUNS_JSON = OPENCLAW_HOME / "agents" / "main" / "subagents" / "runs.json"
# Legacy path some gateways use (GATEWAY-INTEGRATION.md: subagents/runs.json)
RUNS_JSON_LEGACY = OPENCLAW_HOME / "subagents" / "runs.json"
DELEGATIONS_LOG = OPENCLAW_HOME / "logs" / "agent-swarm-delegations.jsonl"
# OverClaw gateway URL for Overstory agent list (GET /api/agents)
GATEWAY_URL = os.environ.get("OVERCLAW_GATEWAY_URL", "http://localhost:18800")

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Dashboard HTML template (defined before routes that use it)
DASHBOARD_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenClaw Subagent Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        :root {
            --bg-primary: #0f1419;
            --bg-secondary: rgba(26, 32, 44, 0.6);
            --bg-glass: rgba(255, 255, 255, 0.05);
            --bg-glass-hover: rgba(255, 255, 255, 0.08);
            --text-primary: #e8eaed;
            --text-secondary: #9aa0a6;
            --accent-blue: #8ab4f8;
            --accent-green: #81c995;
            --accent-orange: #fbbc04;
            --accent-purple: #c58af9;
            --accent-red: #ea4335;
            --border-color: rgba(255, 255, 255, 0.1);
            --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.2);
            --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.3);
            --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.4);
            --blur-sm: blur(8px);
            --blur-md: blur(12px);
            --blur-lg: blur(20px);
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Inter', Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 50%, #0f1419 100%);
            background-attachment: fixed;
            color: var(--text-primary);
            padding: 24px;
            min-height: 100vh;
            line-height: 1.6;
        }
        @media (max-width: 768px) {
            body {
                padding: 16px;
            }
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 32px;
            padding: 24px 32px;
            background: var(--bg-glass);
            backdrop-filter: var(--blur-md);
            -webkit-backdrop-filter: var(--blur-md);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            box-shadow: var(--shadow-md);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .header:hover {
            background: var(--bg-glass-hover);
            box-shadow: var(--shadow-lg);
        }
        h1 {
            color: var(--accent-blue);
            font-size: 28px;
            font-weight: 600;
            letter-spacing: -0.5px;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        @media (max-width: 768px) {
            .header {
                flex-direction: column;
                gap: 16px;
                padding: 20px;
            }
            h1 {
                font-size: 24px;
            }
        }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 10px;
            position: relative;
        }
        .status-indicator::before {
            content: '';
            position: absolute;
            inset: -4px;
            border-radius: 50%;
            opacity: 0;
            transition: opacity 0.3s;
        }
        .status-indicator.active {
            background: var(--accent-green);
            animation: heartbeat 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        .status-indicator.active::before {
            background: var(--accent-green);
            opacity: 0.3;
            animation: ripple 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        .status-indicator.working {
            background: var(--accent-blue);
            animation: heartbeat 0.8s cubic-bezier(0.4, 0, 0.6, 1) infinite;
            box-shadow: 0 0 12px rgba(138, 180, 248, 0.5);
        }
        .status-indicator.working::before {
            background: var(--accent-blue);
            opacity: 0.4;
            animation: ripple 0.8s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        .status-indicator.stalled {
            background: var(--accent-orange);
            animation: pulse 2s ease-in-out infinite;
        }
        .status-indicator.error {
            background: var(--accent-red);
            animation: pulse 1s ease-in-out infinite;
        }
        .status-indicator.idle {
            background: var(--text-secondary);
            opacity: 0.4;
        }
        @keyframes heartbeat {
            0%, 100% { 
                transform: scale(1);
                opacity: 1;
            }
            50% {
                transform: scale(1.15);
                opacity: 0.85;
            }
        }
        @keyframes ripple {
            0% {
                transform: scale(1);
                opacity: 0.3;
            }
            100% {
                transform: scale(2);
                opacity: 0;
            }
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }
        .controls {
            display: flex;
            gap: 12px;
            align-items: center;
        }
        button {
            background: var(--bg-glass);
            backdrop-filter: var(--blur-sm);
            -webkit-backdrop-filter: var(--blur-sm);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            padding: 10px 20px;
            border-radius: 12px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: var(--shadow-sm);
        }
        button:hover {
            background: var(--bg-glass-hover);
            border-color: var(--accent-blue);
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }
        button:active {
            transform: translateY(0) scale(0.98);
        }
        button.active {
            background: linear-gradient(135deg, rgba(138, 180, 248, 0.2), rgba(197, 138, 249, 0.2));
            border-color: var(--accent-blue);
            color: var(--accent-blue);
        }
        .agent-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        @media (max-width: 768px) {
            .agent-grid {
                grid-template-columns: 1fr;
            }
        }
        .agent-card {
            background: var(--bg-glass);
            backdrop-filter: var(--blur-md);
            -webkit-backdrop-filter: var(--blur-md);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: var(--shadow-sm);
            position: relative;
            overflow: hidden;
        }
        .agent-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, transparent, var(--accent-blue), transparent);
            opacity: 0;
            transition: opacity 0.3s;
        }
        .agent-card:hover {
            border-color: var(--accent-blue);
            box-shadow: var(--shadow-lg);
            transform: translateY(-4px);
            background: var(--bg-glass-hover);
        }
        .agent-card:hover::before {
            opacity: 1;
        }
        .agent-card.stalled {
            border-color: var(--accent-orange);
        }
        .agent-card.stalled::before {
            background: linear-gradient(90deg, transparent, var(--accent-orange), transparent);
        }
        .role-badge {
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 4px;
            margin-left: 6px;
            font-weight: 600;
        }
        .role-badge.main {
            background: var(--accent-blue);
            color: var(--bg-dark);
        }
        .role-badge.cron {
            background: var(--text-secondary);
            color: var(--bg-dark);
        }
        .role-badge.overstory {
            background: var(--accent-purple);
            color: var(--bg-primary);
        }
        .agent-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 15px;
        }
        .agent-title {
            font-size: 18px;
            font-weight: 600;
            color: var(--accent-blue);
            margin-bottom: 4px;
        }
        .agent-model {
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: 4px;
        }
        .agent-stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-bottom: 16px;
        }
        .stat {
            background: var(--bg-secondary);
            padding: 12px;
            border-radius: 10px;
            font-size: 12px;
            border: 1px solid var(--border-color);
            transition: all 0.3s;
        }
        .stat:hover {
            background: var(--bg-glass-hover);
            border-color: var(--accent-blue);
        }
        .stat-label {
            color: var(--text-secondary);
            font-size: 11px;
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .stat-value {
            color: var(--text-primary);
            font-weight: 600;
            font-size: 14px;
        }
        .task-progress {
            margin-bottom: 16px;
        }
        .task-label {
            font-size: 12px;
            color: var(--text-secondary);
            margin-bottom: 8px;
        }
        .progress-bar {
            background: var(--bg-secondary);
            height: 8px;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid var(--border-color);
        }
        .progress-fill {
            background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple));
            height: 100%;
            transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 0 12px rgba(138, 180, 248, 0.4);
        }
        .agent-actions {
            display: flex;
            flex-wrap: nowrap;
            gap: 6px;
            margin-top: 15px;
        }
        .agent-actions button,
        .agent-actions a.btn-inspect {
            flex: 1 1 0;
            min-width: 0;
            font-size: 11px;
            padding: 4px 8px;
            border-radius: 8px;
            line-height: 1.1;
        }
        .agent-actions a.btn-inspect {
            display: inline-block;
            text-align: center;
            text-decoration: none;
            color: var(--accent-blue);
            background: var(--bg-glass);
            border: 1px solid var(--border-color);
        }
        .agent-actions a.btn-inspect:hover {
            background: var(--bg-glass-hover);
        }
        .transcript-panel {
            background: var(--bg-glass);
            backdrop-filter: var(--blur-md);
            -webkit-backdrop-filter: var(--blur-md);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 20px;
            margin-top: 20px;
            max-height: 400px;
            overflow-y: auto;
            overflow-x: hidden;
            word-wrap: break-word;
            box-shadow: var(--shadow-md);
        }
        .transcript-panel::-webkit-scrollbar {
            width: 8px;
        }
        .transcript-panel::-webkit-scrollbar-track {
            background: var(--bg-secondary);
            border-radius: 4px;
        }
        .transcript-panel::-webkit-scrollbar-thumb {
            background: var(--border-color);
            border-radius: 4px;
        }
        .transcript-panel::-webkit-scrollbar-thumb:hover {
            background: var(--accent-blue);
        }
        .transcript-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border-color);
        }
        .transcript-events {
            font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
            font-size: 12px;
            line-height: 1.7;
            word-wrap: break-word;
            overflow-wrap: break-word;
            word-break: break-word;
        }
        .event {
            padding: 12px;
            margin-bottom: 10px;
            background: var(--bg-secondary);
            border-left: 3px solid var(--border-color);
            border-radius: 10px;
            word-wrap: break-word;
            overflow-wrap: break-word;
            word-break: break-word;
            max-width: 100%;
            overflow: hidden;
            transition: all 0.3s;
            border: 1px solid transparent;
        }
        .event:hover {
            background: var(--bg-glass-hover);
            border-color: var(--border-color);
            transform: translateX(4px);
        }
        .event.tool-call {
            border-left-color: var(--accent-blue);
        }
        .event.thinking {
            border-left-color: var(--accent-purple);
        }
        .event.result {
            border-left-color: var(--accent-green);
        }
        .event-time {
            color: var(--text-secondary);
            font-size: 11px;
            margin-right: 8px;
        }
        .event-type {
            color: var(--accent-blue);
            font-weight: 600;
            margin-right: 8px;
        }
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #888;
        }
        .empty-state h2 {
            color: #4fc3f7;
            margin-bottom: 10px;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #888;
        }
        .last-update {
            font-size: 12px;
            color: #888;
            margin-top: 10px;
        }
        .color-key {
            background: var(--bg-glass);
            backdrop-filter: var(--blur-md);
            -webkit-backdrop-filter: var(--blur-md);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 24px;
            font-size: 12px;
            box-shadow: var(--shadow-sm);
        }
        .color-key h3 {
            color: var(--accent-blue);
            margin-bottom: 16px;
            font-size: 16px;
            font-weight: 600;
        }
        .color-key-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 12px;
        }
        .color-key-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px;
            border-radius: 8px;
            transition: all 0.2s;
        }
        .color-key-item:hover {
            background: var(--bg-glass-hover);
        }
        .color-key-swatch {
            width: 18px;
            height: 18px;
            border-radius: 4px;
            flex-shrink: 0;
            border: 1px solid var(--border-color);
        }
        .color-key-label {
            color: var(--text-primary);
            font-size: 13px;
        }
        .kanban-board {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 24px;
            margin-bottom: 30px;
        }
        @media (max-width: 768px) {
            .kanban-board {
                grid-template-columns: 1fr;
            }
        }
        .kanban-column {
            background: var(--bg-glass);
            backdrop-filter: var(--blur-md);
            -webkit-backdrop-filter: var(--blur-md);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 20px;
            min-height: 300px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: var(--shadow-sm);
        }
        .kanban-column:hover {
            box-shadow: var(--shadow-md);
        }
        .kanban-column-header {
            font-weight: 600;
            color: var(--accent-blue);
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 16px;
        }
        .kanban-column-count {
            background: var(--bg-secondary);
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            color: var(--text-primary);
            min-width: 24px;
            text-align: center;
        }
        .kanban-task {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
            cursor: pointer;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: var(--shadow-sm);
            position: relative;
        }
        .kanban-task.enter {
            animation: slideIn 0.28s cubic-bezier(0.4, 0, 0.2, 1);
        }
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px) scale(0.95);
            }
            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }
        .kanban-task.moving {
            z-index: 1000;
            animation: cardMove 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        }
        @keyframes cardMove {
            0% {
                transform: scale(1);
                opacity: 1;
            }
            50% {
                transform: scale(1.05) translateY(-10px);
                opacity: 0.8;
            }
            100% {
                transform: scale(1);
                opacity: 1;
            }
        }
        .kanban-task:hover {
            border-color: var(--accent-blue);
            transform: translateY(-4px);
            box-shadow: var(--shadow-md);
            background: var(--bg-glass-hover);
        }
        .kanban-task-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 8px;
        }
        .kanban-task-title {
            font-weight: 600;
            color: #e0e0e0;
            font-size: 14px;
            flex: 1;
            min-width: 0;
            max-height: 4.2em;
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            word-break: break-word;
        }
        .task-description {
            font-size: 12px;
            color: #888;
            margin-top: 10px;
            padding: 8px;
            background: #0a0e27;
            border-radius: 4px;
            max-height: 6em;
            overflow-y: auto;
            word-break: break-word;
        }
        .kanban-task-agent {
            font-size: 11px;
            color: #888;
            margin-top: 4px;
        }
        .kanban-task-progress {
            height: 4px;
            background: #1a1f3a;
            border-radius: 2px;
            margin-top: 8px;
            overflow: hidden;
        }
        .kanban-task-progress-bar {
            height: 100%;
            background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple));
            transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 0 8px rgba(138, 180, 248, 0.3);
        }
        .kanban-task-status {
            font-size: 10px;
            padding: 4px 8px;
            border-radius: 8px;
            background: var(--bg-secondary);
            color: var(--text-secondary);
            font-weight: 600;
            border: 1px solid var(--border-color);
        }
        .view-toggle {
            display: flex;
            gap: 12px;
            margin-bottom: 24px;
        }
        .view-toggle button {
            flex: 1;
        }
        .kanban-column.completed-column,
        .kanban-column.cancelled-column {
            opacity: 0.7;
        }
        .kanban-column.completed-column.collapsed .kanban-column-header,
        .kanban-column.cancelled-column.collapsed .kanban-column-header {
            cursor: pointer;
        }
        .kanban-column.completed-column.collapsed .kanban-task-details,
        .kanban-column.cancelled-column.collapsed .kanban-task-details {
            display: none;
        }
        .kanban-column.completed-column.collapsed .kanban-task,
        .kanban-column.cancelled-column.collapsed .kanban-task {
            padding: 10px 12px;
            min-height: auto;
        }
        .kanban-task-summary .kanban-task-tokens {
            font-size: 11px;
            color: var(--text-secondary);
            margin-top: 6px;
        }
        .kanban-column.completed-column.collapsed .kanban-task-summary .kanban-task-title {
            -webkit-line-clamp: 2;
            max-height: 2.8em;
        }
        .collapse-toggle {
            font-size: 11px;
            color: var(--text-secondary);
            cursor: pointer;
            margin-left: 8px;
            padding: 4px 8px;
            border-radius: 6px;
            transition: all 0.2s;
        }
        .collapse-toggle:hover {
            background: var(--bg-glass-hover);
            color: var(--accent-blue);
        }
        .stalled-reason {
            font-size: 11px;
            color: var(--accent-orange);
            margin-top: 8px;
            padding: 10px;
            background: rgba(251, 188, 4, 0.1);
            border-radius: 8px;
            border-left: 3px solid var(--accent-orange);
            border: 1px solid rgba(251, 188, 4, 0.2);
        }
        .resume-button {
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
            border: none;
            color: var(--bg-primary);
            padding: 5px 8px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 11px;
            font-weight: 600;
            margin-top: 0;
            width: auto;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: var(--shadow-sm);
        }
        .resume-button:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }
        .resume-button:active {
            transform: translateY(0);
        }
        .heartbeat-row {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-top: 8px;
            font-size: 12px;
            color: var(--text-secondary);
        }
        .heartbeat-dot {
            width: 8px;
            height: 8px;
            border-radius: 999px;
            background: var(--text-secondary);
            opacity: 0.5;
        }
        .heartbeat-dot.working,
        .heartbeat-dot.active {
            background: var(--accent-green);
            opacity: 1;
            animation: heartbeat 1.1s ease-in-out infinite;
        }
        .heartbeat-dot.stalled {
            background: var(--accent-orange);
            opacity: 1;
            animation: pulse 1.2s ease-in-out infinite;
        }
        .heartbeat-dot.completed {
            background: var(--accent-blue);
            opacity: 1;
        }
        .heartbeat-dot.idle {
            background: var(--text-secondary);
            opacity: 0.55;
        }
        .console-line {
            margin-top: 8px;
            font-size: 11px;
            color: var(--text-secondary);
            background: rgba(12, 18, 28, 0.55);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 8px 10px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .console-line strong {
            color: var(--accent-blue);
        }
        .btn-resume {
            background: #4fc3f7 !important;
            color: #0a0e27 !important;
        }
        .btn-restart {
            background: #ff9800 !important;
            color: #0a0e27 !important;
        }
        .btn-kill {
            background: #f44336 !important;
            color: #fff !important;
        }
        .task-actions {
            display: flex;
            flex-wrap: nowrap;
            gap: 6px;
            margin-top: 10px;
        }
        .task-actions .resume-button {
            flex: 1 1 0;
            min-width: 0;
            border-radius: 8px;
        }
        .empty-state, .loading {
            text-align: center;
            padding: 60px 20px;
            color: var(--text-secondary);
            background: var(--bg-glass);
            backdrop-filter: var(--blur-sm);
            -webkit-backdrop-filter: var(--blur-sm);
            border: 1px solid var(--border-color);
            border-radius: 16px;
        }
        .empty-state h2, .loading h2 {
            color: var(--accent-blue);
            margin-bottom: 12px;
        }
        .last-update {
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: 8px;
        }
        .project-indicator {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            margin-top: 6px;
            padding: 6px 12px;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            font-size: 13px;
            color: var(--text-secondary);
        }
        .project-indicator .project-icon {
            font-size: 16px;
        }
        .project-indicator .project-label strong {
            color: var(--accent-blue);
        }
        .agent-project-badge {
            display: inline-block;
            font-size: 11px;
            padding: 3px 8px;
            border-radius: 6px;
            background: var(--bg-secondary);
            color: var(--text-secondary);
            margin-bottom: 6px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>🤖 OpenClaw Subagent Dashboard</h1>
            <div class="project-indicator" id="projectIndicator" title="Workspace path for this dashboard">
                <span class="project-icon">📁</span>
                <span class="project-label">Project: <strong id="projectLabel">—</strong></span>
            </div>
            <div class="last-update" id="lastUpdate">Last update: Never</div>
        </div>
        <div class="controls">
            <span class="status-indicator active" id="statusIndicator"></span>
            <button onclick="refreshAll()">🔄 Refresh</button>
            <button onclick="toggleAutoRefresh()" id="autoRefreshBtn">⏸️ Pause</button>
            <button onclick="toggleAutoRequeue()" id="autoRequeueBtn">♻️ Auto-Requeue: Off</button>
        </div>
    </div>

    <div class="color-key">
        <h3>📊 Status & Activity Guide</h3>
        <div class="color-key-grid">
            <div class="color-key-item">
                <div class="color-key-swatch" style="background: var(--accent-blue); animation: heartbeat 0.8s cubic-bezier(0.4, 0, 0.6, 1) infinite;"></div>
                <span class="color-key-label"><strong>In Progress</strong> - Agent actively executing task</span>
            </div>
            <div class="color-key-item">
                <div class="color-key-swatch" style="background: var(--accent-green);"></div>
                <span class="color-key-label"><strong>Queue / To Do</strong> - Waiting for next step/assignment</span>
            </div>
            <div class="color-key-item">
                <div class="color-key-swatch" style="background: var(--text-secondary); opacity: 0.5;"></div>
                <span class="color-key-label"><strong>Completed</strong> - Task finished successfully</span>
            </div>
            <div class="color-key-item">
                <div class="color-key-swatch" style="background: var(--accent-orange);"></div>
                <span class="color-key-label"><strong>Blocked</strong> - Needs intervention or requeue</span>
            </div>
            <div class="color-key-item">
                <div class="color-key-swatch" style="background: #f44336;"></div>
                <span class="color-key-label"><strong>Cancelled</strong> - Manually cancelled jobs</span>
            </div>
            <div class="color-key-item">
                <div class="color-key-swatch" style="border-left: 3px solid var(--accent-blue); background: transparent;"></div>
                <span class="color-key-label"><strong>Tool Call</strong> - Agent calling a tool/function</span>
            </div>
            <div class="color-key-item">
                <div class="color-key-swatch" style="border-left: 3px solid var(--accent-purple); background: transparent;"></div>
                <span class="color-key-label"><strong>Thinking</strong> - Agent reasoning/processing</span>
            </div>
            <div class="color-key-item">
                <div class="color-key-swatch" style="border-left: 3px solid var(--accent-green); background: transparent;"></div>
                <span class="color-key-label"><strong>Result</strong> - Tool result received</span>
            </div>
        </div>
    </div>

    <div class="view-toggle">
        <button onclick="showView('kanban')" id="kanbanBtn" class="active">📋 Kanban Board</button>
        <button onclick="showView('cards')" id="cardsBtn">🎴 Agent Cards</button>
    </div>

    <div id="kanbanView" style="display: block;">
        <div id="kanbanBoard" class="kanban-board">
            <div class="loading">Loading kanban board...</div>
        </div>
    </div>

    <div id="cardsView" style="display: none;">
        <div id="agentGrid" class="agent-grid">
            <div class="loading">Loading subagents...</div>
        </div>
    </div>

    <script>
        let autoRefresh = true;
        let autoRequeue = false;
        let refreshInterval = null;
        let previousAgentPositions = new Map(); // Track agent positions for animations
        let hasRenderedKanban = false;
        let lastKanbanSignature = '';
        const autoRequeueCooldownMs = 2 * 60 * 1000;
        const autoRequeueLastRunBySession = new Map();
        let autoRequeueInFlight = false;

        function formatDuration(ms) {
            if (!ms) return 'unknown';
            const seconds = ms / 1000;
            if (seconds < 60) return seconds.toFixed(1) + 's';
            const minutes = seconds / 60;
            if (minutes < 60) return minutes.toFixed(1) + 'm';
            const hours = minutes / 60;
            return hours.toFixed(1) + 'h';
        }

        function formatTimestamp(ts) {
            if (!ts) return '';
            const date = new Date(ts);
            return date.toLocaleTimeString();
        }

        function escapeHtml(s) {
            if (s == null || s === '') return '';
            const div = document.createElement('div');
            div.textContent = s;
            return div.innerHTML;
        }

        function updateLastUpdate() {
            document.getElementById('lastUpdate').textContent = 
                'Last update: ' + new Date().toLocaleTimeString();
        }

        async function fetchSubagents() {
            try {
                const response = await fetch('/api/subagents');
                if (!response.ok) {
                    console.warn('Subagents API returned', response.status);
                    return [];
                }
                const text = await response.text();
                if (!text || !text.trim()) {
                    console.warn('Subagents API returned empty body');
                    return [];
                }
                const data = JSON.parse(text);
                if (data.gateway_url) window.gatewayUrl = data.gateway_url;
                const projectEl = document.getElementById('projectLabel');
                const indicatorEl = document.getElementById('projectIndicator');
                if (projectEl) projectEl.textContent = data.project || '—';
                if (indicatorEl && data.workspace_path) indicatorEl.title = data.workspace_path;
                return Array.isArray(data.subagents) ? data.subagents : [];
            } catch (error) {
                console.error('Error fetching subagents:', error);
                return [];
            }
        }

        async function fetchTranscript(sessionId) {
            try {
                const response = await fetch(`/api/subagent/${sessionId}/transcript?lines=20`);
                if (!response.ok) {
                    console.error('Transcript fetch failed:', response.status, response.statusText);
                    return [];
                }
                const data = await response.json();
                if (!data || !Array.isArray(data.events)) {
                    console.error('Invalid transcript data format:', data);
                    return [];
                }
                return data.events || [];
            } catch (error) {
                console.error('Error fetching transcript:', error);
                return [];
            }
        }

        function getAgentStatus(agent) {
            // Cancelled jobs get their own column
            const outcomeStatus = (agent.outcomeStatus || (agent.outcome && agent.outcome.status) || '').toString().toLowerCase();
            if (['cancelled', 'canceled', 'killed'].includes(outcomeStatus)) {
                return 'cancelled';
            }
            // Check if task is completed first
            if (agent.completed || agent.endedAt) {
                return 'completed';
            }
            
            const ageMs = agent.ageMs || 0;
            const isStalled = ageMs > 30 * 60 * 1000;   // No activity 30+ min -> blocked
            const hasTask = !!(agent.task && String(agent.task).trim());
            
            if (isStalled) return 'stalled';
            // Agent with a task is "in progress" by nature until completed/cancelled/stalled
            if (hasTask) return 'working';
            // No task: use age to distinguish recently active vs idle (awaiting assignment)
            const isWorking = ageMs < 2 * 60 * 1000;
            const isIdle = ageMs > 5 * 60 * 1000;
            if (isWorking) return 'working';
            if (isIdle) return 'idle';
            return 'active';
        }

        function getKanbanLane(agent) {
            const status = getAgentStatus(agent);
            const outcomeStatus = (agent.outcomeStatus || (agent.outcome && agent.outcome.status) || '').toString().toLowerCase();
            if (status === 'cancelled') return 'cancelled';
            if (status === 'completed') return 'completed';
            if (status === 'stalled' || (outcomeStatus && outcomeStatus !== 'ok')) return 'blocked';
            if (status === 'working') return 'in_progress';
            return 'queue'; // active/idle map to queue
        }

        function getStalledReason(agent, isStalled) {
            if (!isStalled || agent.completed) return '';
            
            const ageMinutes = (agent.ageMs || 0) / 60000;
            let reason = '';
            
            if (agent.outcomeStatus && agent.outcomeStatus !== 'ok') {
                reason = `<div style="font-size: 11px; color: #ff9800; margin-top: 8px; padding: 6px; background: rgba(255, 152, 0, 0.1); border-radius: 4px; border-left: 2px solid #ff9800;">⚠️ Error: ${agent.outcomeStatus || 'Failed'}${agent.outcomeError ? ' - ' + agent.outcomeError : ''}</div>`;
            } else if (ageMinutes > 60) {
                reason = `<div style="font-size: 11px; color: #ff9800; margin-top: 8px; padding: 6px; background: rgba(255, 152, 0, 0.1); border-radius: 4px; border-left: 2px solid #ff9800;">⏱️ Inactive for ${ageMinutes.toFixed(1)} minutes - May be stuck</div>`;
            } else {
                reason = `<div style="font-size: 11px; color: #ff9800; margin-top: 8px; padding: 6px; background: rgba(255, 152, 0, 0.1); border-radius: 4px; border-left: 2px solid #ff9800;">⏸️ No activity for ${ageMinutes.toFixed(1)} minutes</div>`;
            }
            
            return reason;
        }

        function getHeartbeatMeta(agent) {
            const lane = getKanbanLane(agent);
            const ageMinutes = ((agent.ageMs || 0) / 60000).toFixed(1);
            if (lane === 'in_progress') return { dotClass: 'working', text: `Heartbeat: active now (${ageMinutes}m)` };
            if (lane === 'queue') return { dotClass: 'idle', text: `Heartbeat: queued (${ageMinutes}m)` };
            if (lane === 'blocked') return { dotClass: 'stalled', text: `Heartbeat: blocked (${ageMinutes}m)` };
            if (lane === 'cancelled') return { dotClass: 'stalled', text: 'Heartbeat: cancelled' };
            return { dotClass: 'completed', text: 'Heartbeat: completed' };
        }

        function getConsoleText(agent) {
            const lane = getKanbanLane(agent);
            const taskPart = agent.task ? `Task: ${agent.task}` : 'Task: awaiting description';
            if (lane === 'cancelled') return `Cancelled job. ${taskPart}`;
            if (lane === 'completed') return `Completed. ${taskPart}`;
            if (lane === 'blocked') {
                if (agent.outcomeError) return `Stalled: ${agent.outcomeError}`;
                if (agent.outcomeStatus && agent.outcomeStatus !== 'ok') return `Stalled: outcome=${agent.outcomeStatus}`;
                return `Stalled: no updates recently. ${taskPart}`;
            }
            if (lane === 'in_progress') return `Running. ${taskPart}`;
            return `Queued. waiting for assignment/step. ${taskPart}`;
        }

        function renderAgentCard(agent, index) {
            const age = formatDuration(agent.ageMs);
            const taskProgress = agent.taskIndex !== undefined && agent.totalTasks !== undefined
                ? `<div class="task-progress">
                    <div class="task-label">Task ${agent.taskIndex}/${agent.totalTasks}</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${(agent.taskIndex / agent.totalTasks) * 100}%"></div>
                    </div>
                   </div>`
                : '';
            
            const status = getAgentStatus(agent);
            const lane = getKanbanLane(agent);
            const isStalled = lane === 'blocked';
            const isCompleted = lane === 'completed';
            const cardClass = isStalled ? 'agent-card stalled' : 'agent-card';
            const heartbeat = getHeartbeatMeta(agent);
            const consoleText = getConsoleText(agent);
            
            const roleBadge = agent.role === 'main' ? '<span class="role-badge main">Main</span>' : agent.role === 'cron' ? '<span class="role-badge cron">Cron</span>' : (agent.source === 'overstory' ? '<span class="role-badge overstory">Overstory</span>' : '');
            const projectBadge = agent.project ? `<div class="agent-project-badge" title="Context for this agent">📁 ${escapeHtml(agent.project)}</div>` : '';
            return `
                <div class="${cardClass}" id="agent-${agent.sessionId}" data-role="${agent.role || 'subagent'}">
                    <div class="agent-header">
                        <div>
                            <div class="agent-title">Agent ${index + 1} ${roleBadge}</div>
                            ${projectBadge}
                            <div class="agent-model">${agent.model || 'unknown'}</div>
                        </div>
                        <span class="status-indicator ${lane === 'completed' ? 'active' : lane === 'in_progress' ? 'working' : lane === 'queue' ? 'idle' : lane === 'blocked' ? 'stalled' : 'stalled'}" title="${lane === 'in_progress' ? 'In Progress' : lane === 'queue' ? 'Queue' : lane === 'blocked' ? 'Blocked' : lane === 'completed' ? 'Completed' : 'Cancelled'}"></span>
                    </div>
                    <div class="heartbeat-row">
                        <span class="heartbeat-dot ${heartbeat.dotClass}"></span>
                        <span>${heartbeat.text}</span>
                    </div>
                    <div class="agent-stats">
                        <div class="stat">
                            <div class="stat-label">Age</div>
                            <div class="stat-value">${age}</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Input Tokens</div>
                            <div class="stat-value">${agent.inputTokens !== null && agent.inputTokens !== undefined ? agent.inputTokens : 0}</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Output Tokens</div>
                            <div class="stat-value">${agent.outputTokens !== null && agent.outputTokens !== undefined ? agent.outputTokens : 0}</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Session ID</div>
                            <div class="stat-value" style="font-size: 10px; word-break: break-all;">${(agent.sessionId || '').substring(0, 16)}...</div>
                        </div>
                    </div>
                    ${taskProgress}
                    ${agent.task ? `<div class="task-description">${escapeHtml(agent.task)}</div>` : '<div class="task-description" style="color: #ff9800;">⚠️ No task description found</div>'}
                    <div class="console-line"><strong>Console:</strong> ${consoleText}</div>
                    ${(agent.completed && lane !== 'cancelled') ? `<div style="font-size: 11px; color: #4caf50; margin-top: 8px; padding: 6px; background: #0a0e27; border-radius: 4px; border-left: 3px solid #4caf50;">✅ Task completed successfully (session still active - may need cleanup)</div>` : ''}
                    ${getStalledReason(agent, isStalled)}
                    <div class="agent-actions">
                        ${agent.source === 'overstory' ? (window.gatewayUrl ? `<a href="${window.gatewayUrl.replace(/\/$/, '')}/api/agents/${encodeURIComponent(agent.sessionId)}" target="_blank" rel="noopener" class="btn-inspect">🔍 Inspect</a>` : '') : ''}
                        <button onclick="viewTranscript('${agent.sessionId}')">📋 Transcript</button>
                        <button class="btn-resume" onclick="resumeAgent('${agent.sessionId}', '', event)">▶️ Resume</button>
                        <button class="btn-restart" onclick="restartAgent('${agent.sessionId}')">🔄 Restart</button>
                        <button class="btn-kill" onclick="killAgent('${agent.sessionId}')">⛔ Cancel Job</button>
                    </div>
                    <div id="transcript-${agent.sessionId}" class="transcript-panel" style="display: none; margin-top: 15px;">
                        <div class="transcript-header">
                            <strong>Recent Activity</strong>
                            <button onclick="closeTranscript('${agent.sessionId}')">✕</button>
                        </div>
                        <div class="transcript-events" id="transcript-events-${agent.sessionId}" data-loaded="false">
                            Loading...
                        </div>
                    </div>
                </div>
            `;
        }

        async function renderAgents() {
            const grid = document.getElementById('agentGrid');
            const agents = await fetchSubagents();
            
            // Preserve open transcript panels AND their content
            const preservedPanels = new Map();
            document.querySelectorAll('.transcript-panel').forEach(panel => {
                const sessionId = panel.id.replace('transcript-', '');
                const isVisible = panel.style.display !== 'none' && panel.style.display !== '';
                if (isVisible) {
                    const eventsDiv = document.getElementById(`transcript-events-${sessionId}`);
                    preservedPanels.set(sessionId, {
                        visible: true,
                        content: eventsDiv ? eventsDiv.innerHTML : ''
                    });
                }
            });
            
            if (agents.length === 0) {
                grid.innerHTML = `
                    <div class="empty-state">
                        <h2>No Active Subagents</h2>
                        <p>No sessions found. Main and subagents (sessions.json) and gateway-triggered Overstory agents appear here.</p>
                    </div>
                `;
                return;
            }

            grid.innerHTML = agents.map((agent, index) => renderAgentCard(agent, index)).join('');
            
            // Restore preserved transcript panels with their content
            preservedPanels.forEach((data, sessionId) => {
                const panel = document.getElementById(`transcript-${sessionId}`);
                const eventsDiv = document.getElementById(`transcript-events-${sessionId}`);
                if (panel && eventsDiv && data.visible) {
                    panel.style.display = 'block';
                    // Restore the saved content instead of showing "Loading..."
                    if (data.content && data.content !== 'Loading...') {
                        eventsDiv.innerHTML = data.content;
                    }
                }
            });
            
            updateLastUpdate();
        }

        function renderTranscriptEvent(event) {
            const type = event.type || 'unknown';
            let display = '';
            let className = '';
            
            if (type === 'message') {
                const msg = event.message || {};
                const role = msg.role || 'unknown';
                const content = msg.content || [];
                
                // Check for tool calls
                const toolCalls = content.filter(c => c.type === 'toolCall');
                if (toolCalls.length > 0) {
                    className = 'tool-call';
                    display = toolCalls.map(tc => {
                        let argsStr = '';
                        let argsDetails = '';
                        if (tc.arguments) {
                            try {
                                let args;
                                if (typeof tc.arguments === 'string') {
                                    if (tc.arguments === '[object Object]' || tc.arguments.trim() === '') {
                                        argsStr = '';
                                    } else {
                                        args = JSON.parse(tc.arguments);
                                        if (typeof args === 'object' && args !== null) {
                                            argsStr = Object.keys(args).join(', ');
                                            const argValues = Object.entries(args).slice(0, 3).map(([k, v]) => {
                                                const val = typeof v === 'string' ? (v.length > 50 ? v.substring(0, 50) + '...' : v) : JSON.stringify(v).substring(0, 50);
                                                return `${k}=${val}`;
                                            }).join(', ');
                                            if (argValues) argsDetails = ` (${argValues})`;
                                        }
                                    }
                                } else if (typeof tc.arguments === 'object' && tc.arguments !== null) {
                                    argsStr = Object.keys(tc.arguments).join(', ');
                                    const argValues = Object.entries(tc.arguments).slice(0, 3).map(([k, v]) => {
                                        const val = typeof v === 'string' ? (v.length > 50 ? v.substring(0, 50) + '...' : v) : JSON.stringify(v).substring(0, 50);
                                        return `${k}=${val}`;
                                    }).join(', ');
                                    if (argValues) argsDetails = ` (${argValues})`;
                                }
                            } catch (e) {
                                argsStr = '';
                            }
                        }
                        return `🔧 <strong>Calling tool:</strong> ${tc.name || 'tool'}${argsStr ? '<br>  Parameters: ' + argsStr : ''}${argsDetails ? '<br>  Values: ' + argsDetails : ''}`;
                    }).join('<br><br>');
                } else if (role === 'assistant') {
                    className = 'thinking';
                    const text = content.find(c => c.type === 'text')?.text || '';
                    if (text) {
                        display = `💭 <strong>Thinking:</strong><br>${text.substring(0, 500) + (text.length > 500 ? '...' : '')}`;
                    } else {
                        display = '💭 <strong>Processing...</strong>';
                    }
                } else if (role === 'toolResult') {
                    className = 'result';
                    const toolName = msg.toolName || 'tool';
                    let resultPreview = '';
                    try {
                        const resultContent = msg.content || [];
                        const resultText = resultContent.find(c => c.type === 'text')?.text || '';
                        if (resultText) {
                            resultPreview = resultText.substring(0, 200) + (resultText.length > 200 ? '...' : '');
                        } else {
                            resultPreview = JSON.stringify(resultContent).substring(0, 200);
                        }
                    } catch (e) {
                        resultPreview = '[result data]';
                    }
                    display = `✅ <strong>Tool result from ${toolName}:</strong><br>${resultPreview}`;
                } else if (role === 'user') {
                    display = `👤 <strong>User input:</strong><br>${JSON.stringify(content).substring(0, 300)}`;
                } else {
                    try {
                        display = `<strong>${role}:</strong> ${JSON.stringify(content).substring(0, 300)}`;
                    } catch (e) {
                        display = `<strong>${role}:</strong> [content]`;
                    }
                }
            } else {
                try {
                    const eventData = JSON.stringify(event, null, 2).substring(0, 500);
                    display = `<strong>Event (${type}):</strong><br><pre style="font-size: 11px; white-space: pre-wrap; word-wrap: break-word;">${eventData}${eventData.length >= 500 ? '...' : ''}</pre>`;
                } catch (e) {
                    display = `<strong>Event (${type}):</strong> [unable to display]`;
                }
            }
            
            const timestamp = event.timestamp ? formatTimestamp(event.timestamp) : '';
            const eventTypeLabel = type === 'message' ? (className === 'tool-call' ? 'Tool Call' : className === 'thinking' ? 'Thinking' : className === 'result' ? 'Result' : 'Message') : type;
            return `
                <div class="event ${className}">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        ${timestamp ? `<span class="event-time">${timestamp}</span>` : ''}
                        <span class="event-type">${eventTypeLabel}</span>
                    </div>
                    <div style="margin-top: 4px; word-wrap: break-word; overflow-wrap: break-word; word-break: break-word; max-width: 100%; line-height: 1.5;">${display || 'No content'}</div>
                </div>
            `;
        }

        async function viewTranscript(sessionId) {
            const panel = document.getElementById(`transcript-${sessionId}`);
            const eventsDiv = document.getElementById(`transcript-events-${sessionId}`);
            
            if (!panel || !eventsDiv) {
                console.error('Transcript panel not found for session:', sessionId);
                return;
            }
            
            // Toggle panel visibility
            const isVisible = panel.style.display !== 'none' && panel.style.display !== '';
            
            if (isVisible) {
                // Panel is visible, hide it
                panel.style.display = 'none';
                return;
            }
            
            // Panel is hidden, show it and load content
            panel.style.display = 'block';
            
            // Only fetch if content is empty, says "Loading...", or has no children
            const currentContent = eventsDiv.innerHTML.trim();
            if (currentContent === 'Loading...' || currentContent === '' || eventsDiv.children.length === 0) {
                eventsDiv.innerHTML = 'Loading...';
                
                const events = await fetchTranscript(sessionId);
                if (events.length === 0) {
                    eventsDiv.innerHTML = '<div class="event">No transcript events found.</div>';
                    eventsDiv.setAttribute('data-loaded', 'true');
                } else {
                    eventsDiv.innerHTML = events.map(event => renderTranscriptEvent(event)).join('');
                    eventsDiv.setAttribute('data-loaded', 'true');
                }
            } else {
                // Content already loaded, just ensure it's displayed
                if (eventsDiv.getAttribute('data-loaded') !== 'true') {
                    // Content was lost, reload it
                    eventsDiv.innerHTML = 'Loading...';
                    const events = await fetchTranscript(sessionId);
                    if (events.length === 0) {
                        eventsDiv.innerHTML = '<div class="event">No transcript events found.</div>';
                    } else {
                        eventsDiv.innerHTML = events.map(event => renderTranscriptEvent(event)).join('');
                    }
                    eventsDiv.setAttribute('data-loaded', 'true');
                }
            }
        }

        function closeTranscript(sessionId) {
            document.getElementById(`transcript-${sessionId}`).style.display = 'none';
        }

        async function refreshAgent(sessionId) {
            const response = await fetch(`/api/subagent/${sessionId}/refresh`, {
                method: 'POST'
            });
            const data = await response.json();
            alert(data.message || 'Refresh requested');
            renderAgents();
        }

        async function restartAgent(sessionId, options = {}) {
            const skipConfirm = Boolean(options.skipConfirm);
            const silent = Boolean(options.silent);
            // Try to get the task from the agent data
            const agents = await fetchSubagents();
            const agent = agents.find(a => a.sessionId === sessionId);
            const task = agent?.task || '';
            
            const taskPreviewText = String(task || '').substring(0, 100).replace(/["'`]/g, '');
            const taskPreview = taskPreviewText ? ' and restart with: "' + taskPreviewText + '..."' : '';
            if (!skipConfirm && !confirm('Restart this subagent? This will terminate the current session' + taskPreview + '.')) {
                return;
            }
            
            try {
                // First, try to get session key for proper restart
                const statusResponse = await fetch('/api/subagent/' + sessionId + '/status');
                const statusData = await statusResponse.json();
                const session = statusData.session || {};
                const sessionKey = session.key || 'agent:main:subagent:' + sessionId;
                
                // Safely prepare request body
                const requestBody = {
                    sessionKey: sessionKey,
                    task: task
                };
                
                const response = await fetch('/api/subagent/' + sessionId + '/restart', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(requestBody)
                });
                const data = await response.json();
                if (data.success) {
                    if (!silent) alert('Agent restart initiated! Refreshing...');
                    setTimeout(() => {
                        renderKanban();
                        renderAgents();
                    }, 2000);
                } else {
                    if (!silent) alert('Restart failed: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                if (!silent) alert('Error restarting agent: ' + error.message);
            }
        }

        async function killAgent(sessionId) {
            if (!confirm('Cancel this job? This attempts to stop the running subagent.')) {
                return;
            }
            try {
                const response = await fetch('/api/subagent/' + sessionId + '/kill', {
                    method: 'POST'
                });
                const data = await response.json();
                alert(data.message || 'Cancel requested');
                renderKanban();
                renderAgents();
            } catch (error) {
                alert('Error cancelling job: ' + error.message);
            }
        }

        function toggleCompletedColumn(columnKey) {
            const column = document.getElementById(`column-${columnKey}`);
            if (column) {
                column.classList.toggle('collapsed');
            }
        }

        async function resumeAgent(sessionId, sessionKey, event) {
            if (!confirm("Resume this stalled task? This will send a continue message to the agent. If it doesn't resume within 30 seconds, it will be restarted automatically.")) {
                return;
            }
            
            // Get button element for status updates
            const button = event ? event.target : document.getElementById(`resume-${sessionId}`);
            const originalText = button ? button.textContent : '▶️ Resume Task';
            
            try {
                const requestBody = { sessionKey: sessionKey };
                const response = await fetch('/api/subagent/' + sessionId + '/resume', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(requestBody)
                });
                const data = await response.json();
                if (data.success) {
                    // Show loading state
                    if (button) {
                        button.textContent = '⏳ Checking...';
                        button.disabled = true;
                    }
                    
                    alert('Resume message sent! Checking status in 30 seconds...');
                    
                    // Wait 30 seconds, then check if agent resumed
                    setTimeout(async () => {
                        try {
                            // Check if agent has new activity
                            const statusResponse = await fetch(`/api/subagent/${sessionId}/status`);
                            const statusData = await statusResponse.json();
                            const session = statusData.session || {};
                            const updatedAtAfter = session.updatedAt || 0;
                            const updatedAtBefore = data.updated_at_before || 0;
                            
                            // If updatedAt hasn't changed, agent didn't resume
                            if (updatedAtAfter <= updatedAtBefore) {
                                // Resume failed, trigger restart automatically
                                if (confirm('Agent did not resume after 30 seconds. Restart it now?')) {
                                    await restartAgent(sessionId);
                                } else {
                                    if (button) {
                                        button.textContent = originalText;
                                        button.disabled = false;
                                    }
                                }
                            } else {
                                // Agent resumed!
                                alert('✅ Agent resumed successfully!');
                                if (button) {
                                    button.textContent = originalText;
                                    button.disabled = false;
                                }
                                renderKanban();
                                renderAgents();
                            }
                        } catch (checkError) {
                            // If check fails, assume resume failed and restart
                            console.error('Error checking resume status:', checkError);
                            if (confirm('Could not verify if agent resumed. Restart it now?')) {
                                await restartAgent(sessionId);
                            } else {
                                if (button) {
                                    button.textContent = originalText;
                                    button.disabled = false;
                                }
                            }
                        }
                    }, 30000); // Wait 30 seconds
                } else {
                    alert('Failed to resume: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                alert('Error resuming agent: ' + error.message);
                if (button) {
                    button.textContent = originalText;
                    button.disabled = false;
                }
            }
        }

        function refreshAll() {
            const kanbanVisible = document.getElementById('kanbanView').style.display !== 'none';
            if (kanbanVisible) {
                renderKanban();
            } else {
                renderAgents();
            }
        }

        function toggleAutoRefresh() {
            autoRefresh = !autoRefresh;
            const btn = document.getElementById('autoRefreshBtn');
            btn.textContent = autoRefresh ? '⏸️ Pause' : '▶️ Resume';
            
            if (autoRefresh) {
                startAutoRefresh();
            } else {
                stopAutoRefresh();
            }
        }

        function updateAutoRequeueButton() {
            const btn = document.getElementById('autoRequeueBtn');
            if (!btn) return;
            btn.textContent = autoRequeue ? '♻️ Auto-Requeue: On' : '♻️ Auto-Requeue: Off';
            btn.classList.toggle('active', autoRequeue);
        }

        function toggleAutoRequeue() {
            autoRequeue = !autoRequeue;
            try {
                localStorage.setItem('dashboard:autoRequeue', autoRequeue ? '1' : '0');
            } catch (e) {
                // ignore storage errors
            }
            updateAutoRequeueButton();
        }

        async function processAutoRequeue() {
            if (!autoRequeue || autoRequeueInFlight) return;
            autoRequeueInFlight = true;
            try {
                const agents = await fetchSubagents();
                const now = Date.now();
                const blocked = agents.filter(agent => getKanbanLane(agent) === 'blocked');
                // Requeue at most one blocked job per cycle to prevent storms.
                for (const agent of blocked) {
                    const last = autoRequeueLastRunBySession.get(agent.sessionId) || 0;
                    if (now - last < autoRequeueCooldownMs) {
                        continue;
                    }
                    autoRequeueLastRunBySession.set(agent.sessionId, now);
                    await restartAgent(agent.sessionId, { skipConfirm: true, silent: true });
                    break;
                }
            } catch (e) {
                console.error('Auto-requeue error:', e);
            } finally {
                autoRequeueInFlight = false;
            }
        }

        function startAutoRefresh() {
            if (refreshInterval) return;
            refreshInterval = setInterval(async () => {
                if (autoRequeue) {
                    await processAutoRequeue();
                }
                const kanbanVisible = document.getElementById('kanbanView').style.display !== 'none';
                if (kanbanVisible) {
                    renderKanban();
                } else {
                    renderAgents();
                }
            }, 3000); // Refresh every 3 seconds
        }

        function stopAutoRefresh() {
            if (refreshInterval) {
                clearInterval(refreshInterval);
                refreshInterval = null;
            }
        }

        function showView(view) {
            if (view === 'kanban') {
                document.getElementById('kanbanView').style.display = 'block';
                document.getElementById('cardsView').style.display = 'none';
                document.getElementById('kanbanBtn').classList.add('active');
                document.getElementById('cardsBtn').classList.remove('active');
                renderKanban();
            } else {
                document.getElementById('kanbanView').style.display = 'none';
                document.getElementById('cardsView').style.display = 'block';
                document.getElementById('kanbanBtn').classList.remove('active');
                document.getElementById('cardsBtn').classList.add('active');
                renderAgents();
            }
        }

        function computeKanbanSignature(columns) {
            const compact = Object.entries(columns).map(([status, col]) => {
                const items = col.agents
                    .map(agent => ({
                        id: agent.sessionId,
                        status,
                        taskIndex: agent.taskIndex ?? null,
                        totalTasks: agent.totalTasks ?? null,
                        completed: Boolean(agent.completed || agent.endedAt),
                        outcomeStatus: agent.outcomeStatus || (agent.outcome && agent.outcome.status) || null
                    }))
                    .sort((a, b) => (a.id || '').localeCompare(b.id || ''));
                return { status, items };
            });
            return JSON.stringify(compact);
        }

        function renderKanban() {
            const board = document.getElementById('kanbanBoard');
            fetchSubagents().then(agents => {
                const prevPositions = previousAgentPositions;
                // Track current positions
                const currentPositions = new Map();
                
                // Group agents by status
                const columns = {
                    'queue': { title: '🧾 Queue / To Do', agents: [] },
                    'in_progress': { title: '🔄 In Progress', agents: [] },
                    'blocked': { title: '⛔ Blocked', agents: [] },
                    'cancelled': { title: '⛔ Cancelled Jobs', agents: [] },
                    'completed': { title: '✅ Completed', agents: [] }
                };

                agents.forEach(agent => {
                    const lane = getKanbanLane(agent);
                    if (columns[lane]) {
                        columns[lane].agents.push(agent);
                        currentPositions.set(agent.sessionId, lane);
                    }
                });

                // Check for position changes and mark cards for animation
                const cardsToAnimate = new Set();
                currentPositions.forEach((status, sessionId) => {
                    const prevStatus = prevPositions.get(sessionId);
                    if (prevStatus && prevStatus !== status) {
                        cardsToAnimate.add(sessionId);
                    }
                });

                // Avoid full DOM rebuild on every poll tick when nothing meaningful changed.
                const nextSignature = computeKanbanSignature(columns);
                const alreadyRendered = board.dataset.rendered === 'true';
                if (alreadyRendered && nextSignature === lastKanbanSignature) {
                    return;
                }
                lastKanbanSignature = nextSignature;
                board.dataset.rendered = 'true';

                board.innerHTML = Object.entries(columns).map(([key, col]) => {
                    const isCompleted = key === 'completed';
                    const isCancelled = key === 'cancelled';
                    const isBlocked = key === 'blocked';
                    
                    const tasks = col.agents.map((agent, idx) => {
                        const lane = getKanbanLane(agent);
                        const heartbeat = getHeartbeatMeta(agent);
                        const consoleText = getConsoleText(agent);
                        const taskProgress = agent.taskIndex !== undefined && agent.totalTasks !== undefined
                            ? `<div class="kanban-task-progress">
                                <div class="kanban-task-progress-bar" style="width: ${(agent.taskIndex / agent.totalTasks) * 100}%"></div>
                               </div>`
                            : '';
                        
                        const statusBadge = lane === 'in_progress' ? '<span class="kanban-task-status" style="background: #4fc3f7; color: #0a0e27;">In Progress</span>' :
                                          lane === 'queue' ? '<span class="kanban-task-status">Queue</span>' :
                                          lane === 'blocked' ? '<span class="kanban-task-status" style="background: #ff9800; color: #0a0e27;">Blocked</span>' :
                                          lane === 'completed' ? '<span class="kanban-task-status" style="background: #4caf50; color: #0a0e27;">✅ Completed</span>' :
                                          '<span class="kanban-task-status" style="background: #f44336; color: #fff;">⛔ Cancelled</span>';
                        
                        const completedNote = (agent.completed && lane !== 'cancelled') ? '<div style="font-size: 10px; color: #4caf50; margin-top: 4px;">✓ Task completed successfully</div>' : '';
                        
                        // Stalled task reason/error detection
                        let stalledReason = '';
                        if (isBlocked) {
                            const ageMinutes = (agent.ageMs || 0) / 60000;
                            if (agent.outcome && agent.outcome.status !== 'ok') {
                                stalledReason = `<div class="stalled-reason">⚠️ Error: ${agent.outcome.status || 'Failed'} - Task ended with error status</div>`;
                            } else if (agent.completed) {
                                stalledReason = `<div class="stalled-reason">ℹ️ Completed but session still active (needs cleanup)</div>`;
                            } else if (ageMinutes > 60) {
                                stalledReason = `<div class="stalled-reason">⏱️ Inactive for ${ageMinutes.toFixed(1)} minutes - May be stuck or waiting</div>`;
                            } else {
                                stalledReason = `<div class="stalled-reason">⏸️ No activity for ${ageMinutes.toFixed(1)} minutes</div>`;
                            }
                        }
                        
                        const resumeButton = isBlocked && !agent.completed ? 
                            `<button class="resume-button btn-resume" id="resume-${agent.sessionId}" onclick="event.stopPropagation(); resumeAgent('${agent.sessionId}', '', event);">▶️ Resume</button>` :
                            `<button class="resume-button btn-resume" id="resume-${agent.sessionId}" onclick="event.stopPropagation(); resumeAgent('${agent.sessionId}', '', event);">▶️ Resume</button>`;
                        const restartButton = `<button class="resume-button btn-restart" onclick="event.stopPropagation(); restartAgent('${agent.sessionId}')">${isBlocked ? '↩ Requeue' : '🔄 Restart'}</button>`;
                        const killButton = `<button class="resume-button btn-kill" onclick="event.stopPropagation(); killAgent('${agent.sessionId}')">⛔ Cancel Job</button>`;
                        
                        const isMoving = hasRenderedKanban && cardsToAnimate.has(agent.sessionId);
                        const isEntering = hasRenderedKanban && !prevPositions.has(agent.sessionId);
                        const movingClass = isMoving ? 'moving' : '';
                        const enterClass = isEntering ? 'enter' : '';
                        
                        const onClickHandler = (isCompleted || isCancelled) ? '' : `viewTranscript('${agent.sessionId}')`;
                        return `
                            <div class="kanban-task ${movingClass} ${enterClass}" data-session-id="${agent.sessionId}" onclick="${onClickHandler}">
                                <div class="kanban-task-summary">
                                    <div class="kanban-task-header">
                                        <div>
                                            <div class="kanban-task-title" title="${escapeHtml((agent.task || 'No task description').substring(0, 500))}">${escapeHtml(agent.task || 'No task description')} ${agent.role === 'main' ? '<span class="role-badge main">Main</span>' : agent.role === 'cron' ? '<span class="role-badge cron">Cron</span>' : ''}</div>
                                            <div class="kanban-task-agent">Agent ${idx + 1}: ${agent.model || 'unknown'}</div>
                                            ${agent.project ? `<div class="agent-project-badge" style="margin-top: 4px;">📁 ${escapeHtml(agent.project)}</div>` : ''}
                                        </div>
                                        ${statusBadge}
                                    </div>
                                    <div class="kanban-task-tokens">${formatDuration(agent.ageMs)} • ${(agent.inputTokens !== null && agent.inputTokens !== undefined ? agent.inputTokens : 0)}+${(agent.outputTokens !== null && agent.outputTokens !== undefined ? agent.outputTokens : 0)} tokens</div>
                                </div>
                                <div class="kanban-task-details">
                                    ${taskProgress}
                                    <div class="heartbeat-row" style="margin-top: 10px;">
                                        <span class="heartbeat-dot ${heartbeat.dotClass}"></span>
                                        <span>${heartbeat.text}</span>
                                    </div>
                                    <div class="console-line"><strong>Console:</strong> ${consoleText}</div>
                                    ${completedNote}
                                    ${stalledReason}
                                    <div class="task-actions">
                                        ${resumeButton}
                                        ${restartButton}
                                        ${killButton}
                                    </div>
                                </div>
                            </div>
                        `;
                    }).join('');

                    const shouldCollapse = (isCompleted || isCancelled);
                    const collapseToggle = shouldCollapse && col.agents.length > 0 ? 
                        `<span class="collapse-toggle" onclick="event.stopPropagation(); toggleCompletedColumn('${key}');">[collapse]</span>` : '';

                    return `
                        <div class="kanban-column ${isCompleted ? 'completed-column collapsed' : ''} ${isCancelled ? 'cancelled-column collapsed' : ''}" id="column-${key}">
                            <div class="kanban-column-header" ${shouldCollapse ? `onclick="toggleCompletedColumn('${key}')"` : ''}>
                                <span>${col.title}</span>
                                <span style="display: flex; align-items: center; gap: 8px;">
                                    <span class="kanban-column-count">${col.agents.length}</span>
                                    ${collapseToggle}
                                </span>
                            </div>
                            ${tasks || '<div style="color: #888; font-size: 12px; text-align: center; padding: 20px;">No agents in this status</div>'}
                        </div>
                    `;
                }).join('');
                previousAgentPositions = currentPositions;
                hasRenderedKanban = true;
            });
        }

        // Initialize
        try {
            autoRequeue = localStorage.getItem('dashboard:autoRequeue') === '1';
        } catch (e) {
            autoRequeue = false;
        }
        updateAutoRequeueButton();
        renderKanban();
        renderAgents();
        startAutoRefresh();
    </script>
</body>
</html>
'''

def load_sessions():
    """Load sessions.json and return list of session dicts."""
    if not SESSIONS_JSON.exists():
        return []
    try:
        with open(SESSIONS_JSON, 'r') as f:
            data = json.load(f)
        sessions = []
        for key, session in data.items():
            if key.startswith("agent:"):
                session["key"] = key
                sessions.append(session)
        return sessions
    except Exception as e:
        return []

def run_tracker(command, *args, json_output=True):
    """Run subagent-tracker command and return parsed JSON. Pass OPENCLAW_HOME so tracker uses same data as dashboard."""
    cmd = [sys.executable, str(TRACKER_SCRIPT), command] + list(args)
    if json_output:
        cmd.append("--json")
    env = {**os.environ, "OPENCLAW_HOME": str(OPENCLAW_HOME)}
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, env=env, cwd=str(OPENCLAW_HOME))
        if result.returncode != 0:
            return {"error": result.stderr or "Command failed"}
        if json_output:
            return json.loads(result.stdout)
        return result.stdout
    except subprocess.TimeoutExpired:
        return {"error": "Command timed out"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response"}
    except Exception as e:
        return {"error": str(e)}


def _query_overstory_agents(timeout_sec=10):
    """Fetch Overstory agent list from OverClaw gateway GET /api/agents. Returns list of agent dicts or [] on error."""
    url = f"{GATEWAY_URL.rstrip('/')}/api/agents"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            data = json.loads(resp.read().decode())
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, json.JSONDecodeError, ValueError) as e:
        print(f"Overstory agents fetch failed: {e}", file=sys.stderr)
        return []
    if isinstance(data, dict) and data.get("error"):
        return []
    # Gateway may return {"raw": "text"} when overstory status outputs plain text
    if isinstance(data, dict) and "raw" in data and not any(k in data for k in ("agents", "agent", "items", "result")):
        # Parse Overstory status text to extract agent info from worktrees
        raw_text = data.get("raw", "")
        return _parse_overstory_status_text(raw_text)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "agents" in data:
        return data["agents"] if isinstance(data["agents"], list) else []
    for key in ("agents", "agent", "items", "result"):
        if key in data and isinstance(data[key], list):
            return data[key]
    return []


def _parse_overstory_status_text(status_text):
    """Parse Overstory status text output to extract agent info from worktrees.
    Returns list of agent dicts with name, task_id, capability inferred from worktree paths.
    """
    if not status_text:
        return []
    agents = []
    lines = status_text.split('\n')
    in_worktrees = False
    for line in lines:
        line = line.strip()
        if '🌳 Worktrees:' in line or 'Worktrees:' in line:
            in_worktrees = True
            continue
        if in_worktrees:
            if not line or line.startswith('📬') or line.startswith('🔀') or line.startswith('📈'):
                break
            # Parse worktree path: overstory/capability-name/task-id
            # e.g., "overstory/builder-162b29/workspace-57e"
            if line.startswith('overstory/'):
                parts = line.split('/')
                if len(parts) >= 3:
                    capability_part = parts[1]  # e.g., "builder-162b29"
                    task_id = parts[2]  # e.g., "workspace-57e"
                    # Extract capability from name (e.g., "builder-162b29" -> "builder")
                    capability = capability_part.split('-')[0] if '-' in capability_part else capability_part
                    agent_name = capability_part
                    agents.append({
                        "name": agent_name,
                        "capability": capability,
                        "task_id": task_id,
                        "status": "running",  # If worktree exists, assume running
                    })
    return agents


def _overstory_agents_to_dashboard_format(agents_list):
    """Convert Overstory agent list to dashboard session-like format. Each item gets source='overstory'."""
    now_ms = int(time.time() * 1000)
    out = []
    for a in agents_list:
        if not isinstance(a, dict):
            continue
        name = a.get("name") or a.get("agent") or a.get("id") or ""
        if not name:
            continue
        session_id = str(name)
        key = f"overstory:{session_id}"
        task = a.get("task") or a.get("description") or a.get("task_id") or ""
        capability = a.get("capability") or a.get("model") or "overstory"
        status = (a.get("status") or "").strip().lower()
        terminal_statuses = ("completed", "failed", "terminated")
        potentially_complete = ("potentially complete", "potentially_complete", "ok", "success")
        is_terminal = status in terminal_statuses or status in potentially_complete
        updated_at = a.get("updatedAt") or a.get("updated_at") or a.get("start_time") or now_ms
        if isinstance(updated_at, (int, float)):
            updated_at_ms = int(updated_at * 1000) if updated_at < 1e12 else int(updated_at)
        else:
            updated_at_ms = now_ms
        age_ms = max(0, now_ms - updated_at_ms)
        project_label = (a.get("task_id") or a.get("bead_id") or session_id)
        out.append({
            "key": key,
            "sessionId": session_id,
            "role": "subagent",
            "source": "overstory",
            "project": f"Overstory · {project_label}" if project_label else "Overstory",
            "updatedAt": updated_at_ms,
            "ageMs": age_ms,
            "model": capability,
            "task": task if isinstance(task, str) else str(task) if task else "",
            "inputTokens": 0,
            "outputTokens": 0,
            "taskIndex": None,
            "totalTasks": None,
            "completed": is_terminal,
            "outcomeStatus": status if is_terminal else None,
            "displayName": name,
        })
    return out


@app.route('/')
def index():
    """Serve the dashboard HTML."""
    return render_template_string(DASHBOARD_HTML)

@app.route('/favicon.ico')
def favicon():
    """Return 204 No Content for favicon requests."""
    from flask import Response
    return Response(status=204)

def _load_runs_from_path(path):
    """Load runs from a JSON file; return (runs_by_key, runs_by_session_id)."""
    out_key = {}
    out_sid = {}
    if not path.exists():
        return out_key, out_sid
    try:
        with open(path, 'r', encoding='utf-8') as f:
            runs_data = json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}", file=sys.stderr)
        return out_key, out_sid
    runs = runs_data.get("runs", {}) if isinstance(runs_data, dict) else {}
    run_items = list(runs.items()) if isinstance(runs, dict) else [(i, r) for i, r in enumerate(runs) if isinstance(r, dict)] if isinstance(runs, list) else []
    for _rid, run_info in run_items:
        child_key = run_info.get("childSessionKey") or run_info.get("sessionKey")
        session_id = run_info.get("sessionId")
        if not child_key and session_id:
            child_key = f"agent:main:subagent:{session_id}"
        if not child_key:
            continue
        blob = {
            "childSessionKey": child_key,
            "task": run_info.get("task", ""),
            "taskIndex": run_info.get("taskIndex"),
            "totalTasks": run_info.get("totalTasks"),
            "endedAt": run_info.get("endedAt"),
            "outcome": run_info.get("outcome"),
            "cleanup": run_info.get("cleanup", "keep")
        }
        out_key[child_key] = blob
        if session_id:
            out_sid[str(session_id)] = blob
    return out_key, out_sid


def _recent_tasks_by_model(max_lines=1000):
    """Read delegation log and return dict: model_slug -> most recent task string (for fallback when runs.json has no task)."""
    out = {}
    if not DELEGATIONS_LOG.exists():
        return out
    try:
        with open(DELEGATIONS_LOG, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
        return out
    for line in lines[-max_lines:]:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(entry, dict):
            continue
        task = entry.get("task")
        model = entry.get("model") or ""
        if not task or not model:
            continue
        # Normalize model to slug for matching (e.g. openrouter/minimax/minimax-m2.5 -> minimax-m2.5)
        slug = model.split("/")[-1] if "/" in model else model
        out[slug] = task
    return out


def _enrich_agents_with_runs(agents):
    """Enrich agents with task data from RUNS_JSON and legacy subagents/runs.json. Match by key or sessionId."""
    runs_by_key = {}
    runs_by_session_id = {}
    for path in (RUNS_JSON, RUNS_JSON_LEGACY):
        key_map, sid_map = _load_runs_from_path(path)
        runs_by_key.update(key_map)
        runs_by_session_id.update(sid_map)
    
    for agent in agents:
        agent_key = agent.get("key")
        session_id = agent.get("sessionId")
        run_info = None
        if agent_key and agent_key in runs_by_key:
            run_info = runs_by_key[agent_key]
        elif session_id and str(session_id) in runs_by_session_id:
            run_info = runs_by_session_id[str(session_id)]
        if run_info:
            task = run_info.get("task", "")
            if task:
                agent["task"] = task
            agent["taskIndex"] = run_info.get("taskIndex")
            agent["totalTasks"] = run_info.get("totalTasks")
            agent["endedAt"] = run_info.get("endedAt")
            agent["outcome"] = run_info.get("outcome")
            agent["cleanup"] = run_info.get("cleanup", "keep")
            outcome = run_info.get("outcome", {}) if isinstance(run_info.get("outcome"), dict) else {}
            outcome_status = (outcome.get("status") or "").strip().lower()
            completed_statuses = ("ok", "completed", "success")
            is_complete = bool(run_info.get("endedAt")) or outcome_status in completed_statuses
            if is_complete:
                agent["completed"] = True
                if outcome:
                    agent["outcomeStatus"] = outcome.get("status")
                    agent["outcomeError"] = outcome.get("error")
                    agent["outcomeMessage"] = outcome.get("message")
        # Ensure task is always a string; keep tracker/session task if runs didn't provide one
        if "task" not in agent or agent.get("task") is None:
            agent["task"] = ""
        else:
            agent["task"] = str(agent["task"]) if agent["task"] else ""
        # Project/context: OpenClaw agents use workspace name; Overstory agents keep their project from _overstory_agents_to_dashboard_format
        if agent.get("source") != "overstory":
            agent["project"] = agent.get("project") or PROJECT_LABEL
        # Fallback: if still no task, use most recent delegation log task for this model (including main)
        if not agent.get("task"):
            model_slug = (agent.get("model") or "").split("/")[-1] if agent.get("model") else ""
            if model_slug:
                tasks_by_model = _recent_tasks_by_model()
                if model_slug in tasks_by_model:
                    agent["task"] = tasks_by_model[model_slug]
        
        input_tokens = agent.get("inputTokens")
        output_tokens = agent.get("outputTokens")
        agent["inputTokens"] = int(input_tokens) if input_tokens is not None and input_tokens != "null" else 0
        agent["outputTokens"] = int(output_tokens) if output_tokens is not None and output_tokens != "null" else 0
        
        model = agent.get("model")
        if model is None or model == "" or model == "unknown":
            model_override = agent.get("modelOverride")
            provider_override = agent.get("providerOverride")
            if model_override and model_override != "null" and provider_override and provider_override != "null":
                agent["model"] = f"{provider_override}/{model_override}"
            elif model_override and model_override != "null":
                agent["model"] = model_override
            elif provider_override and provider_override != "null":
                agent["model"] = provider_override
            else:
                agent["model"] = model if model else "unknown"
    
    return agents, runs_by_key

@app.route('/api/sessions')
def get_sessions():
    """Get list of active sessions (alias for /api/subagents for compatibility)."""
    result = run_tracker("list", "--active", "60")
    if "error" in result:
        return jsonify({"error": result["error"], "sessions": []}), 500
    
    agents = result if isinstance(result, list) else []
    agents, runs_by_key = _enrich_agents_with_runs(agents)
    
    # Include recently cancelled and recently completed (same as get_subagents)
    active_keys = {a.get("key") for a in agents if a.get("key")}
    now_ms = int(time.time() * 1000)
    recent_window_ms = 24 * 60 * 60 * 1000
    completed_statuses = ("ok", "completed", "success")
    cancelled_statuses = ("cancelled", "canceled", "killed")
    for child_key, run_info in runs_by_key.items():
        if child_key in active_keys:
            continue
        outcome = run_info.get("outcome") if isinstance(run_info, dict) else None
        if not isinstance(outcome, dict):
            continue
        status = str(outcome.get("status", "")).lower()
        ended_at = run_info.get("endedAt")
        if ended_at and isinstance(ended_at, (int, float)) and (now_ms - int(ended_at)) > recent_window_ms:
            continue
        if status in cancelled_statuses:
            pseudo_session_id = child_key.split(":")[-1] if child_key else f"cancelled-{len(agents)+1}"
            agents.append({
                "agentIndex": len(agents) + 1,
                "key": child_key,
                "sessionId": pseudo_session_id,
                "updatedAt": ended_at or now_ms,
                "ageMs": max(0, now_ms - int(ended_at)) if isinstance(ended_at, (int, float)) else 0,
                "model": "unknown",
                "inputTokens": 0,
                "outputTokens": 0,
                "task": run_info.get("task", ""),
                "taskIndex": run_info.get("taskIndex"),
                "totalTasks": run_info.get("totalTasks"),
                "endedAt": ended_at,
                "completed": True,
                "outcome": outcome,
                "outcomeStatus": outcome.get("status"),
                "outcomeError": outcome.get("error"),
                "outcomeMessage": outcome.get("message"),
            })
        elif status in completed_statuses:
            pseudo_session_id = child_key.split(":")[-1] if child_key else f"completed-{len(agents)+1}"
            agents.append({
                "agentIndex": len(agents) + 1,
                "key": child_key,
                "sessionId": pseudo_session_id,
                "updatedAt": ended_at or now_ms,
                "ageMs": max(0, now_ms - int(ended_at)) if isinstance(ended_at, (int, float)) else 0,
                "model": "unknown",
                "inputTokens": 0,
                "outputTokens": 0,
                "task": run_info.get("task", ""),
                "taskIndex": run_info.get("taskIndex"),
                "totalTasks": run_info.get("totalTasks"),
                "endedAt": ended_at,
                "completed": True,
                "outcome": outcome,
                "outcomeStatus": outcome.get("status"),
                "outcomeError": outcome.get("error"),
                "outcomeMessage": outcome.get("message"),
            })
    
    return jsonify({"sessions": agents})


@app.route('/api/project')
def get_project():
    """Lightweight endpoint: current project/workspace label and path for indicators."""
    return jsonify({
        "project": PROJECT_LABEL,
        "workspace_path": str(WORKSPACE_PATH),
    })


@app.route('/api/subagents')
def get_subagents():
    """Get list of all sessions: subagents, main, and optionally cron. Always detects all from sessions.json.
    Query param: minutes=N (optional) to filter to sessions active within N minutes; omit to show all.
    Query param: cron=1 to include cron job sessions."""
    try:
        include_cron = request.args.get("cron", "false").lower() in ("1", "true", "yes")
        args_list = ["--include-main"]
        if include_cron:
            args_list.append("--include-cron")
        minutes = request.args.get("minutes")
        if minutes is not None:
            try:
                m = max(1, min(int(minutes), 43200))
                args_list.extend(["--active", str(m)])
            except ValueError:
                pass
        result = run_tracker("list", *args_list)
        if "error" in result:
            return jsonify({"error": result["error"], "subagents": []}), 500
        
        agents = result if isinstance(result, list) else []
        if not isinstance(agents, list):
            agents = []
        agents, runs_by_key = _enrich_agents_with_runs(agents)
        
        # Include recently cancelled and recently completed jobs even if no longer in sessions list.
        active_keys = {a.get("key") for a in agents if isinstance(a, dict) and a.get("key")}
        now_ms = int(time.time() * 1000)
        recent_window_ms = 24 * 60 * 60 * 1000
        completed_statuses = ("ok", "completed", "success")
        cancelled_statuses = ("cancelled", "canceled", "killed")
        for child_key, run_info in runs_by_key.items():
            if child_key in active_keys:
                continue
            outcome = run_info.get("outcome") if isinstance(run_info, dict) else None
            if not isinstance(outcome, dict):
                continue
            status = str(outcome.get("status", "")).lower()
            ended_at = run_info.get("endedAt")
            if ended_at and isinstance(ended_at, (int, float)) and (now_ms - int(ended_at)) > recent_window_ms:
                continue
            if status in cancelled_statuses:
                pseudo_session_id = child_key.split(":")[-1] if child_key else f"cancelled-{len(agents)+1}"
                agents.append({
                    "agentIndex": len(agents) + 1,
                    "role": "subagent",
                    "key": child_key,
                    "sessionId": pseudo_session_id,
                    "project": PROJECT_LABEL,
                    "updatedAt": ended_at or now_ms,
                    "ageMs": max(0, now_ms - int(ended_at)) if isinstance(ended_at, (int, float)) else 0,
                    "model": "unknown",
                    "inputTokens": 0,
                    "outputTokens": 0,
                    "task": run_info.get("task", ""),
                    "taskIndex": run_info.get("taskIndex"),
                    "totalTasks": run_info.get("totalTasks"),
                    "endedAt": ended_at,
                    "completed": True,
                    "outcome": outcome,
                    "outcomeStatus": outcome.get("status"),
                    "outcomeError": outcome.get("error"),
                    "outcomeMessage": outcome.get("message"),
                })
            elif status in completed_statuses:
                pseudo_session_id = child_key.split(":")[-1] if child_key else f"completed-{len(agents)+1}"
                agents.append({
                    "agentIndex": len(agents) + 1,
                    "role": "subagent",
                    "key": child_key,
                    "sessionId": pseudo_session_id,
                    "project": PROJECT_LABEL,
                    "updatedAt": ended_at or now_ms,
                    "ageMs": max(0, now_ms - int(ended_at)) if isinstance(ended_at, (int, float)) else 0,
                    "model": "unknown",
                    "inputTokens": 0,
                    "outputTokens": 0,
                    "task": run_info.get("task", ""),
                    "taskIndex": run_info.get("taskIndex"),
                    "totalTasks": run_info.get("totalTasks"),
                    "endedAt": ended_at,
                    "completed": True,
                    "outcome": outcome,
                    "outcomeStatus": outcome.get("status"),
                    "outcomeError": outcome.get("error"),
                    "outcomeMessage": outcome.get("message"),
                })
        
        # Merge Overstory agents (gateway-triggered) so they appear in the same view
        overstory_raw = _query_overstory_agents()
        overstory_agents = _overstory_agents_to_dashboard_format(overstory_raw)
        for i, ov in enumerate(overstory_agents):
            ov["agentIndex"] = len(agents) + i + 1
            agents.append(ov)
        
        return jsonify({
            "subagents": agents,
            "gateway_url": GATEWAY_URL,
            "project": PROJECT_LABEL,
            "workspace_path": str(WORKSPACE_PATH),
        })
    except Exception as e:
        print(f"get_subagents error: {e}", file=sys.stderr)
        return jsonify({"error": str(e), "subagents": []}), 500


@app.route('/api/overstory-agents')
def get_overstory_agents():
    """Get Overstory agents from gateway (raw). For debugging or alternate consumers."""
    raw = _query_overstory_agents()
    return jsonify({"overstory_agents": raw})


@app.route('/api/subagent/<session_id>/status')
def get_subagent_status(session_id):
    """Get detailed status for a specific subagent."""
    result = run_tracker("status", session_id)
    if "error" in result:
        return jsonify({"error": result["error"]}), 500
    return jsonify(result)

@app.route('/api/sessions/<session_id>')
def get_session_detail(session_id):
    """Get session details including transcript."""
    # Get status
    status_result = run_tracker("status", session_id)
    if "error" in status_result:
        return jsonify({"error": status_result["error"]}), 500
    
    session_data = status_result.get("session", {})
    
    # Get transcript
    transcript_path = SESSIONS_PATH / f"{session_id}.jsonl"
    events = []
    if transcript_path.exists():
        try:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-50:] if len(all_lines) > 50 else all_lines
                for line in recent_lines:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                        if isinstance(event, dict):
                            events.append(event)
                    except (json.JSONDecodeError, TypeError):
                        continue
        except Exception:
            pass
    
    session_data["transcript"] = events
    return jsonify(session_data)

@app.route('/api/subagent/<session_id>/transcript')
def get_subagent_transcript(session_id):
    """Get transcript for a specific subagent."""
    lines = request.args.get('lines', 50, type=int)
    
    # Read transcript JSONL file directly
    transcript_path = SESSIONS_PATH / f"{session_id}.jsonl"
    events = []
    
    if not transcript_path.exists():
        return jsonify({"error": "Transcript not found", "events": []}), 404
    
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            # Get last N lines
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            
            for line in recent_lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    # Ensure event is a dict and has required structure
                    if isinstance(event, dict):
                        events.append(event)
                except (json.JSONDecodeError, TypeError) as e:
                    # Skip invalid JSON lines
                    continue
    except (IOError, OSError) as e:
        return jsonify({"error": f"Failed to read transcript: {str(e)}", "events": []}), 500
    except Exception as e:
        return jsonify({"error": str(e), "events": []}), 500
    
    return jsonify({"events": events})

@app.route('/api/subagent/<session_id>/refresh', methods=['POST'])
def refresh_subagent(session_id):
    """Refresh/restart a subagent (placeholder - requires gateway access)."""
    # For now, just return success - actual restart would need gateway API
    return jsonify({
        "success": True,
        "message": "Refresh requested (restart requires gateway access)",
        "session_id": session_id
    })

@app.route('/api/subagent/<session_id>/kill', methods=['POST'])
def kill_subagent(session_id):
    """Cancel a subagent job/session.

    Strategy:
    1) Try graceful stop via `openclaw agent --session-id ...` with a stop message.
    2) Force local cleanup fallback by removing the session record and marking run outcome as cancelled.
    Always returns JSON so the client never gets ERR_EMPTY_RESPONSE.
    """
    def fail(err_msg, status=500):
        return jsonify({
            "success": False,
            "message": err_msg,
            "session_id": session_id,
            "session_key": "",
            "graceful_ok": False,
            "removed_from_sessions": False,
            "run_marked_cancelled": False,
            "stderr": "",
            "stdout_preview": "",
        }), status

    try:
        now_ms = int(time.time() * 1000)
        session_key = ""
        graceful_ok = False
        graceful_stdout = ""
        graceful_stderr = ""
        removed_from_sessions = False
        removed_key = ""

        # Resolve session key from sessions store
        try:
            sessions = load_sessions()
            for s in sessions:
                if s.get("sessionId") == session_id:
                    session_key = s.get("key", "")
                    break
        except Exception:
            pass

        # Attempt graceful termination (may hang; keep timeout)
        try:
            stop_msg = "STOP NOW. End this subagent session immediately and do not continue."
            proc = subprocess.run(
                ["openclaw", "agent", "--session-id", session_id, "--message", stop_msg, "--json"],
                capture_output=True,
                text=True,
                timeout=25,
            )
            graceful_stdout = (proc.stdout or "").strip()
            graceful_stderr = (proc.stderr or "").strip()
            graceful_ok = proc.returncode == 0
        except subprocess.TimeoutExpired:
            graceful_stderr = "Command timed out (25s)"
        except Exception as e:
            graceful_stderr = str(e)

        # Force local cleanup in sessions.json
        sessions_path = SESSIONS_JSON
        if sessions_path.exists():
            try:
                with open(sessions_path, "r", encoding="utf-8") as f:
                    sessions_data = json.load(f)
                if isinstance(sessions_data, dict):
                    for key, sess in list(sessions_data.items()):
                        if isinstance(sess, dict) and sess.get("sessionId") == session_id:
                            removed_key = key
                            sessions_data.pop(key, None)
                            removed_from_sessions = True
                            break
                    if removed_from_sessions:
                        with open(sessions_path, "w", encoding="utf-8") as f:
                            json.dump(sessions_data, f, indent=2)
            except Exception:
                pass

        # Mark run as cancelled; create one if missing
        run_marked_cancelled = False
        child_key = removed_key or session_key or f"agent:main:subagent:{session_id}"
        for runs_json_path in (RUNS_JSON, RUNS_JSON_LEGACY):
            try:
                if runs_json_path.exists():
                    with open(runs_json_path, "r", encoding="utf-8") as f:
                        runs_data = json.load(f)
                else:
                    runs_data = {"runs": {}}
                if not isinstance(runs_data.get("runs"), dict):
                    runs_data["runs"] = {}
                runs = runs_data["runs"]
                found = False
                for run_id, run_info in list(runs.items()):
                    if not isinstance(run_info, dict):
                        continue
                    ck = run_info.get("childSessionKey") or run_info.get("sessionKey", "")
                    if (removed_key and ck == removed_key) or (session_id and (session_id in ck or run_info.get("sessionId") == session_id)):
                        run_info["endedAt"] = now_ms
                        run_info["outcome"] = {
                            "status": "cancelled",
                            "message": "Cancelled from dashboard action",
                            "error": "manual_cancel",
                        }
                        run_info["cleanup"] = "done"
                        run_info["childSessionKey"] = child_key
                        run_info["sessionId"] = session_id
                        run_marked_cancelled = True
                        found = True
                        break
                if not found:
                    run_id = f"cancelled-{session_id}"
                    runs[run_id] = {
                        "childSessionKey": child_key,
                        "sessionId": session_id,
                        "task": "",
                        "endedAt": now_ms,
                        "outcome": {
                            "status": "cancelled",
                            "message": "Cancelled from dashboard action",
                            "error": "manual_cancel",
                        },
                        "cleanup": "done",
                    }
                    run_marked_cancelled = True
                runs_data["runs"] = runs
                try:
                    runs_json_path.parent.mkdir(parents=True, exist_ok=True)
                except Exception:
                    pass
                with open(runs_json_path, "w", encoding="utf-8") as f:
                    json.dump(runs_data, f, indent=2)
            except Exception:
                pass

        success = graceful_ok or removed_from_sessions or run_marked_cancelled
        if graceful_ok and removed_from_sessions:
            message = f"Cancelled job {session_id}: graceful stop + forced cleanup applied."
        elif graceful_ok:
            message = f"Cancel signal sent for job {session_id}."
        elif removed_from_sessions or run_marked_cancelled:
            message = f"Forced local cancel applied for job {session_id} (removed from active state)."
        else:
            message = f"Cancel attempt failed for job {session_id}."

        return jsonify({
            "success": success,
            "message": message,
            "session_id": session_id,
            "session_key": session_key or removed_key,
            "graceful_ok": graceful_ok,
            "removed_from_sessions": removed_from_sessions,
            "run_marked_cancelled": run_marked_cancelled,
            "stderr": graceful_stderr[:500] if graceful_stderr else "",
            "stdout_preview": graceful_stdout[:500] if graceful_stdout else "",
        }), (200 if success else 500)
    except Exception as e:
        print(f"kill_subagent error: {e}", file=sys.stderr)
        return fail(f"Cancel failed: {str(e)}", 500)

@app.route('/api/subagent/<session_id>/resume', methods=['POST'])
def resume_subagent(session_id):
    """Resume a stalled subagent by sending a continue message, then check if it resumed."""
    from flask import request as flask_request
    import time
    
    data = flask_request.get_json() or {}
    session_key = data.get("sessionKey", "")
    
    # Try to get session key from runs.json if not provided
    if not session_key:
        runs_json_path = RUNS_JSON
        if runs_json_path.exists():
            try:
                with open(runs_json_path, 'r') as f:
                    runs_data = json.load(f)
                    runs = runs_data.get("runs", {}) if isinstance(runs_data, dict) else {}
                    for run_id, run_info in runs.items():
                        child_key = run_info.get("childSessionKey", "")
                        # Extract session ID from key or find by sessionId
                        if session_id in child_key or child_key.endswith(session_id):
                            session_key = child_key
                            break
            except Exception as e:
                pass
    
    if not session_key:
        # Try to find session key from sessions.json
        try:
            sessions = load_sessions()
            for s in sessions:
                if s.get("sessionId") == session_id:
                    session_key = s.get("key", "")
                    break
        except:
            pass
    
    if not session_key:
        # Try to construct from session_id
        session_key = f"agent:main:subagent:{session_id}"
    
    # Get current agent state before resume attempt
    agent_before = None
    try:
        result = run_tracker("status", session_id)
        if "error" not in result:
            agent_before = result.get("session", {})
            updated_at_before = agent_before.get("updatedAt", 0)
    except:
        updated_at_before = 0
    
    # Note: Actual resume requires sessions_send tool which needs gateway API
    # For now, return instructions but indicate that restart should be attempted if resume fails
    return jsonify({
        "success": True,
        "message": f"Resume message prepared for session {session_id}",
        "session_id": session_id,
        "session_key": session_key,
        "resume_message": "Please continue working on your task.",
        "note": "Resume requires sessions_send tool. If agent doesn't resume within 30 seconds, restart will be triggered.",
        "should_restart_on_failure": True,
        "updated_at_before": updated_at_before
    })

@app.route('/api/subagent/<session_id>/restart', methods=['POST'])
def restart_subagent(session_id):
    """Restart a stalled subagent by terminating and respawning with the same task."""
    from flask import request as flask_request
    
    data = flask_request.get_json() or {}
    session_key = data.get("sessionKey", "")
    task = data.get("task", "")
    
    # Get task from runs.json if not provided
    if not task:
        runs_json_path = RUNS_JSON
        if runs_json_path.exists():
            try:
                with open(runs_json_path, 'r') as f:
                    runs_data = json.load(f)
                    runs = runs_data.get("runs", {}) if isinstance(runs_data, dict) else {}
                    for run_id, run_info in runs.items():
                        child_key = run_info.get("childSessionKey", "")
                        if session_id in child_key or child_key.endswith(session_id) or session_key == child_key:
                            task = run_info.get("task", "")
                            break
            except Exception as e:
                pass
    
    # Note: Actual restart requires gateway API to terminate session and respawn
    # For now, return instructions
    return jsonify({
        "success": True,
        "message": f"Restart requested for session {session_id}",
        "session_id": session_id,
        "session_key": session_key,
        "task": task,
        "note": "Restart requires gateway API to terminate session and respawn with same task. Use sessions_send to terminate, then sessions_spawn to restart."
    })

@app.route('/api/stalled')
def get_stalled():
    """Get list of stalled subagents."""
    result = run_tracker("check", "--stall-minutes", "30")
    if isinstance(result, list):
        return jsonify({"stalled": result})
    return jsonify({"stalled": []})

@app.route('/api/gateway/status')
def get_gateway_status():
    """Get gateway health status via gateway-guard."""
    gateway_guard_script = OPENCLAW_HOME / "workspace" / "skills" / "gateway-guard" / "scripts" / "gateway_guard.py"
    
    if not gateway_guard_script.exists():
        return jsonify({
            "ok": False,
            "running": False,
            "reason": "gateway_guard_script_not_found"
        }), 200
    
    try:
        result = subprocess.run(
            [sys.executable, str(gateway_guard_script), "status", "--json"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(OPENCLAW_HOME),
            env={**os.environ, "OPENCLAW_HOME": str(OPENCLAW_HOME)}
        )
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                status_data = json.loads(result.stdout.strip())
                # Return only safe fields (no secrets)
                return jsonify({
                    "ok": status_data.get("ok", False),
                    "running": status_data.get("running", False),
                    "reason": status_data.get("reason", "unknown"),
                    "recommendedAction": status_data.get("recommendedAction", "none")
                })
            except json.JSONDecodeError as e:
                # Script returned non-JSON output
                error_msg = result.stderr[:200] if result.stderr else result.stdout[:200]
                return jsonify({
                    "ok": False,
                    "running": False,
                    "reason": f"gateway_guard_invalid_json: {error_msg}",
                    "recommendedAction": "check gateway_guard script"
                })
        
        # Script failed - include stderr if available
        error_msg = result.stderr[:200] if result.stderr else "unknown_error"
        if "PermissionError" in error_msg or "Operation not permitted" in error_msg:
            return jsonify({
                "ok": False,
                "running": False,
                "reason": "gateway_guard_permission_error",
                "recommendedAction": "gateway_guard needs system permissions (check Terminal/Full Disk Access)"
            })
        
        # Fallback if script fails or returns invalid JSON
        return jsonify({
            "ok": False,
            "running": False,
            "reason": f"gateway_guard_check_failed (exit {result.returncode}): {error_msg}",
            "recommendedAction": "check gateway manually or gateway_guard script"
        })
    except subprocess.TimeoutExpired:
        return jsonify({
            "ok": False,
            "running": False,
            "reason": "gateway_guard_timeout",
            "recommendedAction": "check gateway manually"
        })
    except Exception as e:
        return jsonify({
            "ok": False,
            "running": False,
            "reason": f"error: {str(e)[:100]}",
            "recommendedAction": "check gateway manually"
        })

@app.route('/api/gateway/config')
def get_gateway_config():
    """Get gateway configuration (port, auth mode) from openclaw.json."""
    config_path = OPENCLAW_HOME / "openclaw.json"
    if not config_path.exists():
        return jsonify({
            "port": 18789,
            "mode": "token"
        }), 200
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        gateway = config.get("gateway", {})
        auth = gateway.get("auth", {})
        return jsonify({
            "port": gateway.get("port", 18789),
            "mode": auth.get("mode", "token")
        })
    except Exception as e:
        return jsonify({
            "port": 18789,
            "mode": "token",
            "error": str(e)[:100]
        }), 200

@app.route('/api/sessions/spawn', methods=['POST'])
def spawn_session():
    """Spawn a new agent session via gateway."""
    data = request.get_json() or {}
    task = data.get("task", "")
    model = data.get("model", "")
    session_target = data.get("sessionTarget", "")
    
    if not task or not model:
        return jsonify({"error": "task and model are required"}), 400
    
    # Use router.py spawn to get proper model routing, then call gateway
    router_script = OPENCLAW_HOME / "workspace" / "skills" / "agent-swarm" / "scripts" / "router.py"
    if router_script.exists():
        try:
            # Run router to get proper model routing
            router_result = subprocess.run(
                [sys.executable, str(router_script), "spawn", "--json", task],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(OPENCLAW_HOME),
                env={**os.environ, "OPENCLAW_HOME": str(OPENCLAW_HOME)}
            )
            if router_result.returncode == 0 and router_result.stdout.strip():
                router_data = json.loads(router_result.stdout.strip())
                model = router_data.get("model", model)
                task = router_data.get("task", task)
                session_target = router_data.get("sessionTarget", session_target)
        except Exception:
            pass  # Fall back to provided values
    
    # For now, return a placeholder - actual spawning would need gateway integration
    # This is a temporary implementation until gateway-attached API exists
    session_id = f"session-{int(time.time())}"
    out = {
        "sessionId": session_id,
        "sessionKey": f"agent:main:subagent:{session_id}",
        "task": task,
        "model": model,
        "note": "Gateway integration pending - this is a placeholder"
    }
    return jsonify(out), 200

@app.route('/api/sessions/<session_id>/send', methods=['POST'])
def send_to_session(session_id):
    """Send a message to a session."""
    data = request.get_json() or {}
    message = data.get("message", "")
    
    if not message:
        return jsonify({"error": "message is required"}), 400
    
    # Placeholder - actual implementation would use gateway sessions_send
    return jsonify({"success": True, "note": "Gateway integration pending"}), 200

@app.route('/api/sessions/<session_id>/kill', methods=['POST'])
def kill_session(session_id):
    """Kill a session."""
    return kill_subagent(session_id)

@app.route('/api/sessions/<session_id>/stream')
def stream_session(session_id):
    """SSE stream for session updates."""
    from flask import Response
    
    def generate():
        # Placeholder SSE stream
        yield f"data: {json.dumps({'type': 'connected', 'sessionId': session_id})}\n\n"
        # In real implementation, would stream transcript updates
        time.sleep(1)
        yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/files/tree')
def get_file_tree():
    """Get file tree for workspace."""
    workspace_path = request.args.get('root') or (OPENCLAW_HOME / "workspace")
    if isinstance(workspace_path, str):
        workspace_path = Path(workspace_path)
    else:
        workspace_path = Path(workspace_path)
    
    def build_tree(path: Path, base: Path) -> list:
        if not path.exists():
            return []
        if path.is_file():
            return [{
                "name": path.name,
                "path": str(path.relative_to(base)),
                "type": "file"
            }]
        children = []
        try:
            for item in sorted(path.iterdir()):
                if item.is_dir():
                    dir_children = build_tree(item, base)
                    children.append({
                        "name": item.name,
                        "path": str(item.relative_to(base)),
                        "type": "directory",
                        "children": dir_children
                    })
                else:
                    children.append({
                        "name": item.name,
                        "path": str(item.relative_to(base)),
                        "type": "file"
                    })
        except PermissionError:
            pass
        return children
    
    tree = build_tree(Path(workspace_path), Path(workspace_path))
    return jsonify(tree)

@app.route('/api/files/content')
def get_file_content():
    """Get file content."""
    path = request.args.get('path')
    if not path:
        return jsonify({"error": "path is required"}), 400
    
    file_path = OPENCLAW_HOME / "workspace" / path.lstrip('/')
    if not file_path.exists() or not file_path.is_file():
        return jsonify({"error": "file not found"}), 404
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({"path": path, "content": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/files/content', methods=['PUT'])
def write_file_content():
    """Write file content."""
    data = request.get_json() or {}
    path = data.get("path")
    content = data.get("content", "")
    
    if not path:
        return jsonify({"error": "path is required"}), 400
    
    file_path = OPENCLAW_HOME / "workspace" / path.lstrip('/')
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/files/content', methods=['DELETE'])
def delete_file():
    """Delete a file."""
    data = request.get_json() or {}
    path = data.get("path")
    
    if not path:
        return jsonify({"error": "path is required"}), 400
    
    file_path = OPENCLAW_HOME / "workspace" / path.lstrip('/')
    try:
        if file_path.exists():
            file_path.unlink()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/files/rename', methods=['POST'])
def rename_file():
    """Rename/move a file."""
    data = request.get_json() or {}
    old_path = data.get("oldPath")
    new_path = data.get("newPath")
    
    if not old_path or not new_path:
        return jsonify({"error": "oldPath and newPath are required"}), 400
    
    old_file = OPENCLAW_HOME / "workspace" / old_path.lstrip('/')
    new_file = OPENCLAW_HOME / "workspace" / new_path.lstrip('/')
    
    try:
        new_file.parent.mkdir(parents=True, exist_ok=True)
        old_file.rename(new_file)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/git/status')
def get_git_status():
    """Get git status."""
    workspace_path = request.args.get('path') or (OPENCLAW_HOME / "workspace")
    if isinstance(workspace_path, str):
        workspace_path = Path(workspace_path)
    
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "--branch"],
            cwd=str(workspace_path),
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return jsonify({"error": "not a git repository"}), 404
        
        staged = []
        unstaged = []
        untracked = []
        branch = "main"
        
        for line in result.stdout.split('\n'):
            if line.startswith('##'):
                # Branch line
                branch = line.split('...')[0].replace('##', '').strip()
            elif line:
                status = line[:2]
                path = line[3:]
                if status[0] != ' ':
                    staged.append({"path": path, "status": "modified"})
                if status[1] != ' ':
                    if status[1] == '?':
                        untracked.append({"path": path, "status": "untracked"})
                    else:
                        unstaged.append({"path": path, "status": "modified"})
        
        return jsonify({
            "branch": branch,
            "ahead": 0,  # Would need git log to calculate
            "behind": 0,
            "staged": staged,
            "unstaged": unstaged,
            "untracked": untracked
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/git/stage', methods=['POST'])
def stage_files():
    """Stage files."""
    data = request.get_json() or {}
    paths = data.get("paths", [])
    workspace_path = OPENCLAW_HOME / "workspace"
    
    try:
        subprocess.run(
            ["git", "add"] + paths,
            cwd=str(workspace_path),
            timeout=5
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/git/unstage', methods=['POST'])
def unstage_files():
    """Unstage files."""
    data = request.get_json() or {}
    paths = data.get("paths", [])
    workspace_path = OPENCLAW_HOME / "workspace"
    
    try:
        subprocess.run(
            ["git", "reset", "HEAD"] + paths,
            cwd=str(workspace_path),
            timeout=5
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/git/commit', methods=['POST'])
def commit_changes():
    """Commit staged changes."""
    data = request.get_json() or {}
    message = data.get("message", "")
    workspace_path = OPENCLAW_HOME / "workspace"
    
    if not message:
        return jsonify({"error": "message is required"}), 400
    
    try:
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=str(workspace_path),
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            return jsonify({"error": result.stderr}), 500
        
        # Get commit hash
        hash_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(workspace_path),
            capture_output=True,
            text=True,
            timeout=5
        )
        hash_value = hash_result.stdout.strip() if hash_result.returncode == 0 else ""
        
        return jsonify({"success": True, "hash": hash_value})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/git/push', methods=['POST'])
def push_changes():
    """Push to remote."""
    branch = request.args.get('branch')
    workspace_path = OPENCLAW_HOME / "workspace"
    
    try:
        cmd = ["git", "push"]
        if branch:
            cmd.extend(["origin", branch])
        subprocess.run(cmd, cwd=str(workspace_path), timeout=30)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/git/pull', methods=['POST'])
def pull_changes():
    """Pull from remote."""
    workspace_path = OPENCLAW_HOME / "workspace"
    
    try:
        subprocess.run(["git", "pull"], cwd=str(workspace_path), timeout=30)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/git/log')
def get_commit_log():
    """Get commit history."""
    limit = int(request.args.get('limit', 50))
    workspace_path = OPENCLAW_HOME / "workspace"
    
    try:
        result = subprocess.run(
            ["git", "log", f"-{limit}", "--pretty=format:%H|%s|%an|%at"],
            cwd=str(workspace_path),
            capture_output=True,
            text=True,
            timeout=5
        )
        
        commits = []
        for line in result.stdout.split('\n'):
            if line:
                parts = line.split('|')
                if len(parts) >= 4:
                    commits.append({
                        "hash": parts[0],
                        "message": parts[1],
                        "author": parts[2],
                        "date": int(parts[3]),
                        "files": []
                    })
        
        return jsonify(commits)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/git/branches')
def get_branches():
    """Get list of branches."""
    workspace_path = OPENCLAW_HOME / "workspace"
    
    try:
        result = subprocess.run(
            ["git", "branch", "--format=%(refname:short)"],
            cwd=str(workspace_path),
            capture_output=True,
            text=True,
            timeout=5
        )
        branches = [b.strip() for b in result.stdout.split('\n') if b.strip()]
        return jsonify(branches)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/git/checkout', methods=['POST'])
def checkout_branch():
    """Switch branch."""
    data = request.get_json() or {}
    branch = data.get("branch")
    workspace_path = OPENCLAW_HOME / "workspace"
    
    if not branch:
        return jsonify({"error": "branch is required"}), 400
    
    try:
        subprocess.run(
            ["git", "checkout", branch],
            cwd=str(workspace_path),
            timeout=5
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))  # Default to 8080 to avoid macOS AirPlay conflict
    print(f"Starting Subagent Dashboard on http://localhost:{port}")
    print(f"OpenClaw Home: {OPENCLAW_HOME}")
    app.run(host='0.0.0.0', port=port, debug=True)
