import curses
import sys
import subprocess

def kill(line):
    line = line.split(" ")
    line=[i for i in line if i.strip()][1]
    subprocess.run(["kill", "-9", line])

def main(stdscr, input_lines):
    stdscr.clear()
    
    if curses.has_colors():
        curses.use_default_colors()
        
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, -1)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        
        default_color = curses.color_pair(1)
        selected_color = curses.color_pair(2) | curses.A_REVERSE
    else:
        default_color = curses.A_NORMAL
        selected_color = curses.A_REVERSE
    
    curses.curs_set(0)

    
    

    current_row = 0

    while True:
        stdscr.clear()

        for idx, line in enumerate(input_lines):
            if idx == current_row:
                stdscr.addstr(idx, 0, f"> {line}", selected_color)
            else:
                stdscr.addstr(idx, 0, f"  {line}", default_color)

        stdscr.refresh()

        key = stdscr.getch()
        match key:
            case curses.KEY_UP if current_row > 0:
                current_row -= 1
            case curses.KEY_DOWN if current_row < len(input_lines) - 1:
                current_row += 1
            case 10:  # Enter key
                line_to_execute = input_lines[current_row]
                kill(line_to_execute)

                input_lines.pop(current_row)
                if not input_lines : exit()

                if current_row >= len(input_lines) and current_row > 0:
                    current_row -= 1
            case 113 : #q key (ord('q'))
                break

PROCESSES_TO_IGNORE = (f"grep {sys.argv[1]}")

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