"""
数据库表结构定义
"""

# 学习目标表
GOALS_TABLE = """
CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    parent_id INTEGER,
    priority TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'active',
    progress REAL DEFAULT 0,
    deadline TEXT,
    estimated_hours INTEGER DEFAULT 0,
    completed_hours INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES goals(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_goals_parent ON goals(parent_id);
CREATE INDEX IF NOT EXISTS idx_goals_status ON goals(status);
"""

# 学习计划表
PLANS_TABLE = """
CREATE TABLE IF NOT EXISTS plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    scheduled_date TEXT NOT NULL,
    estimated_minutes INTEGER DEFAULT 30,
    status TEXT DEFAULT 'pending',
    completed_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_plans_goal ON plans(goal_id);
CREATE INDEX IF NOT EXISTS idx_plans_date ON plans(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_plans_status ON plans(status);
"""

# 复习卡片表
CARDS_TABLE = """
CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal_id INTEGER,
    front TEXT NOT NULL,
    back TEXT NOT NULL,
    tags TEXT,
    ease_factor REAL DEFAULT 2.5,
    interval INTEGER DEFAULT 0,
    repetitions INTEGER DEFAULT 0,
    next_review TEXT,
    last_review TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_cards_goal ON cards(goal_id);
CREATE INDEX IF NOT EXISTS idx_cards_next_review ON cards(next_review);
"""

# 复习记录表
REVIEWS_TABLE = """
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL,
    quality INTEGER NOT NULL,
    reviewed_at TEXT DEFAULT CURRENT_TIMESTAMP,
    time_spent INTEGER,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_reviews_card ON reviews(card_id);
"""

# 学习资源表
RESOURCES_TABLE = """
CREATE TABLE IF NOT EXISTS resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT,
    resource_type TEXT DEFAULT 'article',
    tags TEXT,
    goal_id INTEGER,
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_resources_goal ON resources(goal_id);
CREATE INDEX IF NOT EXISTS idx_resources_type ON resources(resource_type);
"""

# 学习时长记录表
SESSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal_id INTEGER NOT NULL,
    start_time TEXT DEFAULT CURRENT_TIMESTAMP,
    end_time TEXT,
    duration INTEGER DEFAULT 0,
    notes TEXT,
    FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_sessions_goal ON sessions(goal_id);
CREATE INDEX IF NOT EXISTS idx_sessions_time ON sessions(start_time);
"""

# 配置表
CONFIG_TABLE = """
CREATE TABLE IF NOT EXISTS config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

SCHEMAS = [
    GOALS_TABLE,
    PLANS_TABLE,
    CARDS_TABLE,
    REVIEWS_TABLE,
    RESOURCES_TABLE,
    SESSIONS_TABLE,
    CONFIG_TABLE,
]

# 默认配置
DEFAULT_CONFIG = [
    ("user.name", "", "用户姓名"),
    ("review.daily_limit", "20", "每日复习卡片上限"),
    ("review.new_cards_per_day", "10", "每日新卡片上限"),
    ("plan.default_duration", "30", "默认学习任务时长(分钟)"),
]
