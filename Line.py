
class Line :
    def __init__(self, line : str) :
        self.line = "  " + line

        self.command = self.line.split()[10]
        index = self.line.index(self.command)
        self.cmd_range = index, index + len(self.command)

        self.exec_name = self.command.split("/")[-1]

class Matched_Line(Line) :
    def __init__(self, line: str, searched_keyword: str, case_sensitive=False):
        super().__init__(line)
        searched_keyword_index = self.line.index(searched_keyword) if case_sensitive else self.line.lower().index(searched_keyword.lower())
        self.searched_keyword_range = (searched_keyword_index, searched_keyword_index + len(searched_keyword))
        self.breakpoints = sorted([*self.searched_keyword_range, *self.cmd_range, 0])
    @staticmethod
    def from_Line(line : Line, searched_keyword: str, case_sensitive=False) :
        return Matched_Line(line.line[2:], searched_keyword, case_sensitive)