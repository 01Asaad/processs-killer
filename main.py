from argparse import ArgumentParser
import curses
import os
import pwd
import subprocess

from Block import Block, trunc_left, trunc_right
from Highlight import Highlight
from Line import Line

def kill(line : Line):

    processID=[i for i in line.line.split(" ") if i.strip()][1]
    subprocess.run(["kill", "-9", processID])

def get_curses_colors_colored_terminal() :
    curses.use_default_colors()

    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, -1)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)

    curses.init_pair(3, curses.COLOR_YELLOW, -1)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)

    curses.init_pair(5, curses.COLOR_RED, -1)
    curses.init_pair(6, curses.COLOR_RED, curses.COLOR_BLACK)

    default_color = curses.color_pair(1)
    selected_color = curses.color_pair(2) | curses.A_REVERSE
    command_color = curses.color_pair(3) | curses.A_BOLD
    selected_command_color = curses.color_pair(4) | curses.A_BOLD | curses.A_REVERSE
    searched_color = curses.color_pair(5) | curses.A_BOLD
    selected_searched_color = curses.color_pair(6) | curses.A_BOLD | curses.A_REVERSE

    return default_color, selected_color, command_color, selected_command_color, searched_color, selected_searched_color

def get_curses_colors_non_colored_terminal() :
    default_color = curses.A_NORMAL
    selected_color = curses.A_REVERSE
    command_color = curses.A_BOLD
    selected_command_color = curses.A_BOLD | curses.A_REVERSE
    searched_color = curses.A_BOLD
    selected_searched_color = curses.A_BOLD | curses.A_REVERSE
    return default_color, selected_color, command_color, selected_command_color, searched_color, selected_searched_color

def get_curses_colors():
    colors = get_curses_colors_colored_terminal() if curses.has_colors() else get_curses_colors_non_colored_terminal()
    curses.curs_set(0)
    return colors

def get_matching_processes(search_term : str, user_only: bool = False):
    process_output = subprocess.check_output(["ps", "aux"], text=True)
    current_pid = str(os.getpid())
    current_user = pwd.getpwuid(os.getuid()).pw_name

    for line in process_output.splitlines():
        fields = line.split(None, 10)
        if len(fields) < 11 or fields[1] == current_pid:
            continue
        if user_only and fields[0] != current_user:
            continue
        if search_term in line:
            yield line




def draw_line(stdscr, display_line_idx, width, top_row, current_row, start, colors) :
    
    idx = top_row + display_line_idx
    if idx >= len(input_lines): return False

    default_color, selected_color, command_color, selected_command_color, searched_color, selected_searched_color = colors
    base_color = (selected_color, selected_command_color, selected_searched_color) if idx == current_row else (default_color, command_color, searched_color)

    line : Line = input_lines[idx]    

    blocks = line.blocks
    if idx == current_row : blocks = [Block("> ")] + trunc_left(blocks, 2)
    if start > 0 : blocks = [Block("...", Highlight.normal)] + trunc_left(blocks, start + 3)
    if start + width < len(line.line) : blocks = trunc_right(blocks, len(line.line) - (start + width) + 3) + [Block("...", Highlight.normal)]

    try :
        chars_written = 0
        for block in blocks :
            stdscr.addstr(display_line_idx, chars_written, block.content, base_color[block.highlight.value])
            chars_written += len(block.content)
    except curses.error:
        pass


def main(stdscr, input_lines : list[Line]):
    stdscr.clear()


    current_row = 0
    top_row = 0
    h_offset = 0

    COLORS = get_curses_colors()

    while True:
        stdscr.clear()
        if not input_lines: exit()

        visible_height, w = stdscr.getmaxyx()

        top_row = current_row if current_row < top_row else top_row
        top_row = current_row - visible_height + 1 if current_row >= top_row + visible_height else top_row


        max_content_length = max(len(line.line) for line in input_lines)
        max_offset = max(0, max_content_length - w)
        h_offset = max(0, h_offset)
        h_offset = min(h_offset, max_offset)

        for display_line_idx in range(visible_height):
            draw_line(stdscr, display_line_idx, w, top_row, current_row, h_offset, COLORS)

        stdscr.refresh()

        key = stdscr.getch()
        match key:
            case curses.KEY_UP if current_row > 0:
                current_row -= 1
            case curses.KEY_DOWN if current_row < len(input_lines) - 1:
                current_row += 1
            case curses.KEY_RIGHT:
                h_offset = min(max_offset, h_offset + 10)
            case curses.KEY_LEFT:
                h_offset = max(0, h_offset - 10)
            case curses.KEY_END:
                current_row = len(input_lines) - 1
            case curses.KEY_HOME:
                current_row = 0
            case 10:  # Enter key
                line_to_execute = input_lines[current_row]
                kill(line_to_execute)

                input_lines.pop(current_row)
                if not input_lines : exit()

                if current_row >= len(input_lines) and current_row > 0:
                    current_row -= 1
            case 113 : #q key (ord('q'))
                break




if __name__ == '__main__':
    parser = ArgumentParser(description="Process Killer")
    parser.add_argument("search_term", help="Search term for processes")
    parser.add_argument("--exec-only", "-e", action="store_true", help="Only search in the executable path of the process")
    parser.add_argument("--user-only", "-u", action="store_true", help="Only search processes owned by the current user")
    args = parser.parse_args()
    if not args.search_term:
        print("no search term for process was given")
        exit()
    input_lines = [Line(line, args.search_term) for line in get_matching_processes(args.search_term, args.user_only)]
    if args.exec_only :
        input_lines = [line for line in input_lines if args.search_term in line.command]
    if not input_lines :
        print("no processes found")
        exit()
    try : curses.wrapper(main, input_lines)
    except KeyboardInterrupt:
        print("KeyboardInterrupt")