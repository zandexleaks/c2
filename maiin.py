mimport curses
import time
import json
import os
from typing import Dict, Tuple

# Define the menu structure with ASCII art
MENUS: Dict[str, Dict[str, Tuple[str, ...]]] = {
    "start": {
        "normal": (
            "┌─┐┌┬┐┌─┐┬─┐┌┬┐",
            "└─┐ │ ├─┤├┬┘ │ ",
            "└─┘ ┴ ┴ ┴┴└─ ┴ "
        ),
        "selected": (
            "╔═╗╔╦╗╔═╗╦═╗╔╦╗",
            "╚═╗ ║ ╠═╣╠╦╝ ║ ",
            "╚═╝ ╩ ╩ ╩╩╚═ ╩ "
        )
    },
    "options": {
        "normal": (
            "┌─┐┌─┐┌┬┐┬┌─┐┌┐┌┌─┐",
            "│ │├─┘ │ ││ ││││└─┐",
            "└─┘┴   ┴ ┴└─┘┘└┘└─┘"
        ),
        "selected": (
            "╔═╗╔═╗╔╦╗╦╔═╗╔╗╔╔═╗",
            "║ ║╠═╝ ║ ║║ ║║║║╚═╗",
            "╚═╝╩   ╩ ╩╚═╝╝╚╝╚═╝"
        )
    },
    "help": {
        "normal": (
            "┬ ┬┌─┐┬  ┌─┐",
            "├─┤├┤ │  ├─┘",
            "┴ ┴└─┘┴─┘┴  "
        ),
        "selected": (
            "╦ ╦╔═╗╦  ╔═╗",
            "╠═╣║╣ ║  ╠═╝",
            "╩ ╩╚═╝╩═╝╩  "
        )
    },
    "proxies": {
        "normal": (
            "┌─┐┬─┐┌─┐─┐ ┬┬┌─┐┌─┐",
            "├─┘├┬┘│ │┌┴┬┘│├┤ └─┐",
            "┴  ┴└─└─┘┴ └─┴└─┘└─┘"
        ),
        "selected": (
            "╔═╗╦═╗╔═╗═╗ ╦╦╔═╗╔═╗",
            "╠═╝╠╦╝║ ║╔╩╦╝║║╣ ╚═╗",
            "╩  ╩╚═╚═╝╩ ╚═╩╚═╝╚═╝"
        )
    }
}

BANNER = [
    "▄████▄   █    ██  ██▀███    ██████ ▓█████  ▒██▀ ▀█  ",
    "▒██▀ ▀█   ██  ▓██▒▓██ ▒ ██▒▒██    ▒ ▓█   ▀  ▒▓█    ─",
    "▒▓█    ▄ ▓██  ▒██░▓██ ░▄█ ▒░ ▓██▄   ▒███    ▒▓▓▄ ▄██",
    "▒▓▓▄ ▄██▒▓▓█  ░██░▒██▀▀█▄    ▒   ██▒▒▓█  ▄  ▒ ▓███▀ ",
    "▒ ▓███▀ ░▒▒█████▓ ░██▓ ▒██▒▒██████▒▒░▒████▒ ░ ░▒ ▒  ",
    "░ ░▒ ▒  ░░▒▓▒ ▒ ▒ ░ ▒▓ ░▒▓░▒ ▒▓▒ ▒ ░░░ ▒░ ░   ░  ▒  ",
    "  ░  ▒   ░░▒░ ░ ░   ░▒ ░ ▒░░ ░▒  ░ ░ ░ ░  ░ ░       ",
    "░         ░░░ ░ ░   ░░   ░ ░  ░  ░     ░  ░ ░     ",
    "░ ░         ░         ░           ░     ░  ░         ",
    "░                                                   "
]

def create_gradient_colors(num_colors):
    """ Create gradient colors from blue to purple. """
    colors = []
    for i in range(num_colors):
        b = int(1000 * (i / (num_colors - 1)))
        r = int(1000 * (1 - i / (num_colors - 1)))
        g = 0
        try:
            curses.init_color(20 + i, r, g, b)
            curses.init_pair(1 + i, 20 + i, curses.COLOR_BLACK)
            colors.append(curses.color_pair(1 + i))
        except curses.error:
            continue
    return colors

def is_terminal_size_valid(stdscr):
    """ Check the size of the terminal and return True if valid. """
    h, w = stdscr.getmaxyx()
    return h >= 24 and w >= 80

def draw_resize_message(stdscr):
    """ Draw the message asking user to resize the terminal. """
    stdscr.clear()
    message = "Window too small. Please resize to a minimum of 80x24."
    stdscr.addstr(0, 0, message)
    stdscr.refresh()

def draw_menu(stdscr, selected_index, gradient_offset):
    """ Draw the main menu. """
    if not is_terminal_size_valid(stdscr):
        draw_resize_message(stdscr)
        return  # Skip drawing the menu

    stdscr.clear()
    h, w = stdscr.getmaxyx()
    banner_height = len(BANNER) + 2
    total_height = banner_height + len(MENUS) * 4
    start_y = (h - total_height) // 2
    start_x = w // 2
    num_colors = 100
    gradient_colors = create_gradient_colors(num_colors)

    # Draw the banner
    for i, line in enumerate(BANNER):
        if start_y + 1 + i < h:
            banner_x = start_x - len(line) // 2
            for j, char in enumerate(line):
                if banner_x + j < w:
                    color = gradient_colors[(j + i + gradient_offset) % num_colors]
                    stdscr.addstr(start_y + 1 + i, banner_x + j, char, color)

    # Draw the menu items
    for idx, (key, states) in enumerate(MENUS.items()):
        title = key.capitalize()
        title_lines = states["selected"] if idx == selected_index else states["normal"]
        title_x = start_x - len(title) // 2
        
        if start_y + banner_height + idx * 4 < h:
            for j, char in enumerate(title):
                color = gradient_colors[(j + gradient_offset) % num_colors]
                stdscr.addstr(start_y + banner_height + idx * 4, title_x + j, char, color)

            for i, line in enumerate(title_lines):
                if start_y + banner_height + idx * 4 + i + 1 < h:
                    line_x = start_x - len(line) // 2
                    for j, char in enumerate(line):
                        color = gradient_colors[(j + i + gradient_offset) % num_colors]
                        if line_x + j < w:
                            stdscr.addstr(start_y + banner_height + idx * 4 + i + 1, line_x + j, char, color)

    stdscr.addstr(h - 1, 0, "Press Ctrl+C to quit", curses.A_BOLD)
    stdscr.refresh()

def draw_options_page(stdscr, gradient_offset, settings):
    """ Draw the options page. """
    if not is_terminal_size_valid(stdscr):
        draw_resize_message(stdscr)
        return  # Skip drawing the options page

    stdscr.clear()
    h, w = stdscr.getmaxyx()
    num_colors = 100
    gradient_colors = create_gradient_colors(num_colors)
    
    box_height = 15
    box_width = 50
    start_y = (h - box_height) // 2
    start_x = (w - box_width) // 2
    
    # Draw box
    for i in range(box_width):
        color = gradient_colors[(i + gradient_offset) % num_colors]
        stdscr.addstr(start_y, start_x + i, '═' if 0 < i < box_width - 1 else '╔' if i == 0 else '╗', color)
        stdscr.addstr(start_y + box_height - 1, start_x + i, '═' if 0 < i < box_width - 1 else '╚' if i == 0 else '╝', color)
    
    for i in range(1, box_height - 1):
        color_left = gradient_colors[(i + gradient_offset) % num_colors]
        color_right = gradient_colors[(i + gradient_offset + box_width) % num_colors]
        stdscr.addstr(start_y + i, start_x, '║', color_left)
        stdscr.addstr(start_y + i, start_x + box_width - 1, '║', color_right)
    
    stdscr.addstr(start_y + 1, start_x + 1, "Proxy Settings", curses.A_BOLD)
    
    # Draw proxy settings
    proxy_settings = settings.get('proxies', {})
    option_start_row = 3
    for idx, (key, value) in enumerate(proxy_settings.items()):
        setting_line = f"{key}: {value}"
        stdscr.addstr(start_y + option_start_row + idx, start_x + 1, setting_line)

    stdscr.addstr(start_y + box_height - 2, start_x + 1, "Press 'q' to go back", curses.A_BOLD)
    stdscr.refresh()

def main(stdscr):
    """ Main function to run the menu and options interface. """
    curses.curs_set(0)  # Disable cursor
    stdscr.clear()
    settings = {}
    
    # Load settings from a JSON file
    try:
        if os.path.exists('settings.json'):
            with open('settings.json', 'r') as f:
                settings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error reading settings file. Default settings will be used.")
    
    selected_index = 0
    gradient_offset = 0

    while True:
        draw_menu(stdscr, selected_index, gradient_offset)
        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected_index = (selected_index - 1) % len(MENUS)
        elif key == curses.KEY_DOWN:
            selected_index = (selected_index + 1) % len(MENUS)
        elif key == ord('\n'):
            selected = list(MENUS.keys())[selected_index]
            if selected == "proxies":
                draw_options_page(stdscr, gradient_offset, settings)
                while True:
                    key = stdscr.getch()
                    if key == ord('q'):
                        break  # Return to the main menu
                    gradient_offset = (gradient_offset + 1) % 100
                    time.sleep(0.1)
        gradient_offset = (gradient_offset + 1) % 100
        time.sleep(0.1)

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("Exited.")
