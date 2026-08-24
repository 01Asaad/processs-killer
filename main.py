import curses
import sys
import subprocess

PROCESSES_TO_IGNORE = (f"grep {sys.argv[1]}", __file__, "killer " + sys.argv[1])

def kill(line):
    line = line.split(" ")
    line=[i for i in line if i.strip()][1]
    subprocess.run(["kill", "-9", line])

def get_curses_colors():
    if curses.has_colors():
        curses.use_default_colors()

        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, -1)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)

        default_color = curses.color_pair(1)
        selected_color = curses.color_pair(2) | curses.A_REVERSE
        command_color = curses.color_pair(3) | curses.A_BOLD
        selected_command_color = curses.color_pair(4) | curses.A_BOLD | curses.A_REVERSE
    else:
        default_color = curses.A_NORMAL
        selected_color = curses.A_REVERSE
        command_color = curses.A_BOLD
        selected_command_color = curses.A_BOLD

    curses.curs_set(0)
    return default_color, selected_color, command_color, selected_command_color


def get_command_span(line : str, prefix_len : int):
    parts = line.split()
    if len(parts) < 11:
        return None, None

    cmd_name = parts[10]
    cmd_start = line.index(cmd_name)

    return prefix_len + cmd_start, prefix_len + cmd_start + len(cmd_name)


def draw_line(stdscr, display_line_idx, width, top_row, current_row, h_offset):
    
    idx = top_row + display_line_idx
    if idx >= len(input_lines): return False

    default_color, selected_color, command_color, selected_command_color = get_curses_colors()
    base_color = (selected_color, selected_command_color) if idx == current_row else (default_color, command_color)

    line = input_lines[idx]
    prefix = "> " if idx == current_row else "  "

    content : str = prefix + line
    start = h_offset
    
    exec_range = get_command_span(line, len(prefix)) #relative to all line
    exec_range = max(0, exec_range[0] - start), max(0, exec_range[1] - start)

    # shown_line = [""] * width
    shown_line = [i for i in content[start:start + width]]
    if start > 0 : shown_line[:3] = "..."
    if start + width < len(content) : shown_line[-3:] = "..."

    shown_line = "".join(shown_line)

    try :
        if exec_range[0] > 0 :
            stdscr.addstr(display_line_idx, 0, shown_line[:exec_range[0]], base_color[0])
        if exec_range[0] < width and exec_range[1] > 0 :
            stdscr.addstr(display_line_idx, exec_range[0], shown_line[exec_range[0]:exec_range[1]], base_color[1])
        if exec_range[1] < width :
            stdscr.addstr(display_line_idx, exec_range[1], shown_line[exec_range[1]:], base_color[0])
    except curses.error:
        pass


def main(stdscr, input_lines):
    stdscr.clear()
    
    
    current_row = 0
    top_row = 0
    h_offset = 0

    while True:
        stdscr.clear()
        if not input_lines: exit()

        visible_height, w = stdscr.getmaxyx()

        top_row = current_row if current_row < top_row else top_row
        top_row = current_row - visible_height + 1 if current_row >= top_row + visible_height else top_row


        max_content_length = max(len(f"> {line}") for line in input_lines)
        max_offset = max(0, max_content_length - w)
        h_offset = max(0, h_offset)
        h_offset = min(h_offset, max_offset)

        for display_line_idx in range(visible_height):
            draw_line(stdscr, display_line_idx, w, top_row, current_row, h_offset)

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
    if not len(sys.argv) > 1 :
        print("no search term for process inserted")
        exit()
    input_lines = [line for line in subprocess.check_output(f"ps aux | grep {sys.argv[1]}", shell=True, text=True).splitlines() if not any(p in line for p in PROCESSES_TO_IGNORE)]
    if not input_lines :
        print("no processes found")
        exit()
    try : curses.wrapper(main, input_lines)
    except KeyboardInterrupt:
        print("KeyboardInterrupt")