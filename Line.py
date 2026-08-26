from functools import cache
from Highlight import Highlight
from Block import Block, group_blocks_by_highlight

class Line :
    def __init__(self, line : str, searched_keyword : str) :
        self.line = "  " + line
        self.cmd_range = self.get_command_span(line, 2)
        self.searched_keyword_range = (line.index(searched_keyword) + 2, line.index(searched_keyword) + 2 + len(searched_keyword))
        self._blocks = None
    def get_command_span(self, line : str, prefix_len : int):
        parts = line.split()
        cmd_name = parts[10]
        cmd_start = line.index(cmd_name)
        return prefix_len + cmd_start, prefix_len + cmd_start + len(cmd_name)
    @property
    def command(self) :
        if self.cmd_range[0] is None : return None
        return self.line[self.cmd_range[0]:self.cmd_range[1]]
    @property
    def blocks(self) :
        if self._blocks is not None : return self._blocks

        self._blocks : list[Block] = []
        if self.cmd_range[0] is None :
            self._blocks.append(Block(self.line, Highlight.normal))
            return self._blocks

        for i, char in enumerate(self.line) :
            if self.searched_keyword_range[0] <= i < self.searched_keyword_range[1] :
                self._blocks.append(Block(char, Highlight.searched))
            elif self.cmd_range[0] <= i < self.cmd_range[1] :
                self._blocks.append(Block(char, Highlight.command))
            else :
                self._blocks.append(Block(char, Highlight.normal))
        
        self._blocks = group_blocks_by_highlight(self._blocks)

        return self._blocks
    
