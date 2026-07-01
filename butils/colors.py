"""ANSI terminal colors and styled logging formatter."""

import logging

# --- ANSI escape codes ---
RESET = '\033[0m'
BOLD = '\033[1m'
DIM = '\033[2m'

# Foreground
BLACK = '\033[30m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
WHITE = '\033[37m'
GRAY = '\033[90m'

# Bright foreground
BRIGHT_RED = '\033[91m'
BRIGHT_GREEN = '\033[92m'
BRIGHT_YELLOW = '\033[93m'
BRIGHT_BLUE = '\033[94m'
BRIGHT_MAGENTA = '\033[95m'
BRIGHT_CYAN = '\033[96m'
BRIGHT_WHITE = '\033[97m'

# Backgrounds
BG_RED = '\033[41m'
BG_GREEN = '\033[42m'
BG_YELLOW = '\033[43m'
BG_BLUE = '\033[44m'
BG_MAGENTA = '\033[45m'
BG_CYAN = '\033[46m'

LEVEL_COLORS = {
    logging.DEBUG: DIM + GRAY,
    logging.INFO: CYAN,
    logging.WARNING: YELLOW,
    logging.ERROR: RED,
    logging.CRITICAL: RED + BOLD,
}


class ColorFormatter(logging.Formatter):
    """Colorized log formatter matching the existing format."""

    def format(self, record):
        color = LEVEL_COLORS.get(record.levelno, '')
        s = super().format(record)
        return f'{color}{s}{RESET}'
