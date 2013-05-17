from markdownextensions.tests.utils import MarkdownTestCase
from markdownextensions.codeblocks import CodeBlockExtension


class TestCodeBlock(MarkdownTestCase):
    extensions = [CodeBlockExtension()]

    def test_should_find_codeblock(self):
        self.assertMDEquals(u"```Python\n"
                            u"Hello, World\n"
                            u"Out there\n"
                            u"```\n",
                            u'<pre><code class="python">Hello, World\n'
                            u"Out there</code></pre>")
