import curses
import os
import pwd
import subprocess
from argparse import ArgumentParser
from enum import StrEnum

from Line import Line, Matched_Line


def kill(line : Line):

    processID=[i for i in line.line.split(" ") if i.strip()][1]
    subprocess.run(["kill", "-9", processID], check=True)

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
class Search_Target(StrEnum) :
    ALL = "all"
    EXEC_NAME = "exec_name"
    EXEC_PATH = "exec_path"
def get_matching_processes(search_term : str, user_only: bool = False, case_sensitive = False, search_target = Search_Target.ALL, exact_match = False):
    process_output = subprocess.check_output(["ps", "aux"], text=True)
    current_pid = str(os.getpid())
    current_user = pwd.getpwuid(os.getuid()).pw_name
    search_term = search_term if case_sensitive else search_term.lower()

    lines : list[Matched_Line] = []
    for i, row in enumerate(process_output.splitlines()):
        if i == 0 : continue

        fields = row.split(None, 10)
        if len(fields) < 11 or fields[1] == current_pid:
            continue
        if user_only and fields[0] != current_user:
            continue

        line = Line(row)

        match search_target :
            case Search_Target.EXEC_NAME :
                dest = line.exec_name
            case Search_Target.EXEC_PATH :
                dest = line.command
            case Search_Target.ALL :
                dest = row
        if not case_sensitive :
            dest = dest.lower()
            search_term = search_term.lower()

        if exact_match and len(search_term) != len(dest) : continue

        if search_term in dest :
            lines.append(Matched_Line.from_Line(line, search_term, case_sensitive))
    return lines




def draw_line(stdscr, display_line_idx, width, top_row, current_row, start, colors) :
    
    idx = top_row + display_line_idx
    if idx >= len(lines): return False

    default_color, selected_color, command_color, selected_command_color, searched_color, selected_searched_color = colors
    base_color = (selected_color, selected_command_color, selected_searched_color) if idx == current_row else (default_color, command_color, searched_color)

    line : Matched_Line = lines[idx]
    res = line.line
    if start > 0 : res = "..." + res[start + 3:]
    elif idx == current_row : res = "> " + res[2:]
    if width < len(res) : res = res[:width-3] + "..."

    try :
        breakpoints = [0] + [i-start for i in line.breakpoints if i>start]
        for i in breakpoints :
            next_step = next((j for j in breakpoints if j > i), len(res))

            if line.searched_keyword_range[1] > start + 3 and (line.searched_keyword_range[0] - start) <= i < (line.searched_keyword_range[1] - start) : highlight = 2
            elif line.searched_keyword_range[1] > start + 3 and (line.cmd_range[0] - start) <= i < (line.cmd_range[1] - start) : highlight = 1
            else : highlight = 0
            
            chars_to_write = res[i:min(next_step, width)]
            stdscr.addstr(display_line_idx, i, chars_to_write, base_color[highlight])
            if next_step > i+len(chars_to_write) : break
    except curses.error:
        pass
def killall(lines : list[Matched_Line]) :
    count, total = 0, len(lines)
    for line in lines :
        try :
            kill(line)
            count +=1
        except subprocess.CalledProcessError : pass
    print(f"killed {count} processes out of {total}")
def killer_ui(stdscr, lines : list[Matched_Line]):
    stdscr.clear()


    current_row = 0
    top_row = 0
    h_offset = 0

    COLORS = get_curses_colors()

    while True:
        stdscr.clear()
        if not lines: exit()

        visible_height, w = stdscr.getmaxyx()

        top_row = min(top_row, current_row)
        top_row = current_row - visible_height + 1 if current_row >= top_row + visible_height else top_row


        max_content_length = max(len(line.line) for line in lines)
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
            case curses.KEY_DOWN if current_row < len(lines) - 1:
                current_row += 1
            case curses.KEY_RIGHT:
                h_offset = min(max_offset, h_offset + 10)
            case curses.KEY_LEFT:
                h_offset = max(0, h_offset - 10)
            case curses.KEY_HOME:
                current_row = 0
            case curses.KEY_END:
                current_row = len(lines) - 1
            case 97 : #a
                h_offset = 0
            case 100 : #d
                h_offset = (len(lines[current_row].line) - w + 4) if h_offset or len(lines[current_row].line) > h_offset + w else h_offset
            case 102 : #f
                h_offset = max_offset
            case 10:  # Enter key
                line_to_execute = lines[current_row]
                try :kill(line_to_execute)
                except subprocess.CalledProcessError :
                    pass

                lines.pop(current_row)
                if not lines : exit()

                if current_row >= len(lines) and current_row > 0:
                    current_row -= 1
            case 113 : #q key (ord('q'))
                break

def get_parser() :
    parser = ArgumentParser(description="Process Killer")
    
    parser.add_argument("search_term", help="Search term for processes")
    parser.add_argument("--path-only", "-p", action="store_true", help="Only search in the executable path of the process")
    parser.add_argument("--exec-only", "-e", action="store_true", help="Only search in the executable name of the process")
    parser.add_argument("--user-only", "-u", action="store_true", help="Only search processes owned by the current user")
    parser.add_argument("--case-sensitive", "-cs", action="store_true", help="Make the matching case sensitive. by default, if the search term is in lowercasem, it's case insensitive, other wise it is.")
    parser.add_argument("--exact-match", "-x", action="store_true", help="Match whole string instead of substring")
    parser.add_argument("--all", "-a", action="store_true", help="kill all processes with matched criteria, kinda similar behavior to killall command")

    return parser


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    if not args.search_term:
        print("no search term for process was given")
        exit()
    if args.exec_only :
        search_target = Search_Target.EXEC_NAME
    elif args.path_only :
        search_target = Search_Target.EXEC_PATH
    else :
        search_target = Search_Target.ALL
    IS_CASE_SENSITIVE = args.case_sensitive or any(c.isupper() for c in args.search_term)
    lines = get_matching_processes(args.search_term, args.user_only, IS_CASE_SENSITIVE, search_target, args.exact_match)
    if args.exec_only :
        lines = [line for line in lines if args.search_term in line.command]
    if not lines :
        print("no processes found for input " + args.search_term)
        exit()
    if args.all :
        killall(lines)
    else :
        try : curses.wrapper(killer_ui, lines)
        except KeyboardInterrupt:
            print("KeyboardInterrupt")