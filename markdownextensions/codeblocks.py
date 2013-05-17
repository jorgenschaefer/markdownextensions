import re

from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
from markdown import util


class CodeBlockExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.parser.blockprocessors.add('codeblock',
                                      CodeBlockParser(md.parser),
                                      '<code')


class CodeBlockParser(BlockProcessor):
    """Process Github-style code blocks."""

    def test(self, parent, block):
        return block.startswith("```")

    def run(self, parent, blocks):
        block = blocks.pop(0)
        m = re.match("^```(.*)\n", block)
        lang = m.group(1)
        block = block[m.end(0):]

        data = []

        while "\n```" not in block:
            data.append(block)
            if not blocks:
                raise RuntimeError("Code block not closed")
            block = blocks.pop(0)

        rest_code, next_block = block.split("\n```", 1)
        data.append(rest_code)
        if next_block:
            blocks.insert(0, next_block)

        pre = util.etree.SubElement(parent, 'pre')
        code = util.etree.SubElement(pre, 'code')
        if lang:
            code.attrib['class'] = lang.lower()
        code.text = util.AtomicString("\n".join(data))
