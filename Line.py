from enum import IntEnum
from functools import cache


@cache
def get_command_span(line : str, prefix_len : int):
    parts = line.split()
    if len(parts) < 11:
        return None, None

    cmd_name = parts[10]
    cmd_start = line.index(cmd_name)

    return prefix_len + cmd_start, prefix_len + cmd_start + len(cmd_name)


class Highlight(IntEnum) :
    normal = 0
    command = 1
    searched = 2

class Block :
    def __init__(self, content : str, highlight : Highlight = Highlight.normal) :
        self.content = content
        self.highlight = highlight

class Line :
    def __init__(self, line : str, searched_keyword : str) :
        self.line = "  " + line
        self.cmd_range = get_command_span(line, 2)
        self.searched_keyword_range = (line.index(searched_keyword) + 2, line.index(searched_keyword) + 2 + len(searched_keyword))
        self._blocks = None
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

        if self.searched_keyword_range[0] < self.cmd_range[0] :
            self._blocks.append(Block(self.line[:self.searched_keyword_range[0]], Highlight.normal))
            self._blocks.append(Block(self.line[self.searched_keyword_range[0]:self.searched_keyword_range[1]], Highlight.searched))
            self._blocks.append(Block(self.line[self.searched_keyword_range[1]:self.cmd_range[0]], Highlight.normal))
            self._blocks.append(Block(self.line[self.cmd_range[0]:self.cmd_range[1]], Highlight.command))
            self._blocks.append(Block(self.line[self.cmd_range[1]:], Highlight.normal))
        else :
            self._blocks.append(Block(self.line[:self.cmd_range[0]], Highlight.normal))
            self._blocks.append(Block(self.line[self.cmd_range[0]:self.cmd_range[1]], Highlight.command))
            self._blocks.append(Block(self.line[self.cmd_range[1]:self.searched_keyword_range[0]], Highlight.normal))
            self._blocks.append(Block(self.line[self.searched_keyword_range[0]:self.searched_keyword_range[1]], Highlight.searched))
            self._blocks.append(Block(self.line[self.searched_keyword_range[1]:], Highlight.normal))

        return self._blocks
    
def trunc_left(blocks : list[Block], num : int) :
    new_blocks = [Block(b.content, b.highlight) for b in blocks]
    while num > 0 and len(new_blocks) > 0 :
        block = new_blocks[0]
        if len(block.content) <= num :
            num -= len(block.content)
            new_blocks.pop(0)
        else :
            block.content = block.content[num:]
            num = 0
    return new_blocks
def trunc_right(blocks : list[Block], num : int) :
    new_blocks = [Block(b.content, b.highlight) for b in blocks]
    while num > 0 and len(new_blocks) > 0 :
        block = new_blocks[-1]
        if len(block.content) <= num :
            num -= len(block.content)
            new_blocks.pop()
        else :
            block.content = block.content[:-num]
            num = 0
    return new_blocks
