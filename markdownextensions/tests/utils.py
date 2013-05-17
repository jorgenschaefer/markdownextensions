import markdown

import unittest


class MarkdownTestCase(unittest.TestCase):
    extensions = []

    def assertMDEquals(self, markdowntext, html):
        md = markdown.Markdown(extensions=self.extensions)
        self.assertEquals(md.convert(markdowntext), html)
