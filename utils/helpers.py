import random
from datetime import datetime

def generate_screening_id():
    """Generates a realistic border screening audit ID."""
    seq = random.randint(100000, 999999)
    year = datetime.now().year
    return f"BG-{year}-{seq}"

def get_current_timestamp():
    """Returns current timestamp formatted string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
