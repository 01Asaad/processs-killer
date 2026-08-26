from Highlight import Highlight


class Block :
    def __init__(self, content : str, highlight : Highlight = Highlight.normal) :
        self.content = content
        self.highlight = highlight
        
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
def group_blocks_by_highlight(blocks : list[Block]) :
    if not blocks : return []

    grouped_blocks = []
    current_block = Block(blocks[0].content, blocks[0].highlight)

    for block in blocks[1:] :
        if block.highlight == current_block.highlight :
            current_block.content += block.content
        else :
            grouped_blocks.append(current_block)
            current_block = Block(block.content, block.highlight)

    grouped_blocks.append(current_block)
    return grouped_blocks