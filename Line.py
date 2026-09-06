
class Line :
    def __init__(self, line : str, searched_keyword : str, case_sensitive = False) :
        self.line = "  " + line
        self.cmd_range = self.get_command_span(self.line)
        searched_keyword_index = self.line.index(searched_keyword) if case_sensitive else self.line.lower().index(searched_keyword.lower())
        self.searched_keyword_range = (searched_keyword_index, searched_keyword_index + len(searched_keyword))
        self.breaks = sorted([*self.searched_keyword_range, *self.cmd_range, 0])
    def get_command_span(self, line : str, prefix_len : int = 0):
        parts = line.split()
        cmd_name = parts[10]
        cmd_start = line.index(cmd_name)
        return prefix_len + cmd_start, prefix_len + cmd_start + len(cmd_name)
    @property
    def command(self) :
        if self.cmd_range[0] is None : return None
        return self.line[self.cmd_range[0]:self.cmd_range[1]]