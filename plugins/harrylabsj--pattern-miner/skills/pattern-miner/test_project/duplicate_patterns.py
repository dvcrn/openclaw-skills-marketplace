"""Test project for pattern miner."""

def process_data(data):
    """Process data with validation."""
    result = []
    for item in data:
        if item.get('valid'):
            result.append(transform(item))
    return result

def filter_users(users):
    """Filter users with validation."""
    result = []
    for user in users:
        if user.get('active'):
            result.append(transform(user))
    return result

def calculate_stats(numbers):
    """Calculate statistics."""
    total = 0
    count = 0
    for num in numbers:
        total += num
        count += 1
    return total / count if count > 0 else 0

def compute_average(values):
    """Compute average."""
    total = 0
    count = 0
    for val in values:
        total += val
        count += 1
    return total / count if count > 0 else 0

# Another duplicate pattern
def setup_database(config):
    """Setup database connection."""
    import sqlite3
    conn = sqlite3.connect(config['db_path'])
    cursor = conn.cursor()
    return conn, cursor

def init_storage(options):
    """Initialize storage connection."""
    import sqlite3
    conn = sqlite3.connect(options['path'])
    cursor = conn.cursor()
    return conn, cursor
