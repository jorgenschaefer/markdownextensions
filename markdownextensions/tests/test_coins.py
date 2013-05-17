# coding: utf-8

from markdownextensions.tests.utils import MarkdownTestCase
from markdownextensions.metadata import MetaDataExtension
from markdownextensions.coins import COinSExtension


class TestCOinS(MarkdownTestCase):
    extensions = [MetaDataExtension(),
                  COinSExtension()]

    def test_should_add_coins_data(self):
        self.assertMDEquals(u"Title: Test Title\n"
                            u"Author: Jorgen Schäfer\n"
                            u"\n"
                            u"Hello, World\n",
                            u"<p>Hello, World</p>\n"
                            u'<span class="Z3988" title="ctx_ver=Z39.88-2004'
                            u'&amp;rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3A'
                            u'dc&amp;rft.type=blogPost&amp;rft.format=text'
                            u'&amp;rft.au=Jorgen+Sch%C3%A4fer&amp;rft.title='
                            u'Test+Title"></span>')
