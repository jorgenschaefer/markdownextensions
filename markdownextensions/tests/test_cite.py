# coding: utf-8

import os
import tempfile

from markdownextensions.tests.utils import MarkdownTestCase
from markdownextensions.cite import CiteExtension


class TestCOinS(MarkdownTestCase):
    extensions = [CiteExtension()]

    def test_should_add_coins_data(self):
        fd, filename = tempfile.mkstemp(prefix='md-test-')
        self.addCleanup(os.remove, filename)
        fobj = os.fdopen(fd, "w")
        fobj.write(BIBLIOGRAPHY)
        fobj.close()
        markdowntext = """\
Hello, World {{John 2004, p. 23}}
"""
        html = """\
<p>Hello, World <a href="#John 2004">(John 2004, p. 23)</a>
"""
        self.assertMDEquals(markdowntext, html)


BIBLIOGRAPHY = """
"""
