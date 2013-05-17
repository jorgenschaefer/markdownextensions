# coding: utf-8

from markdown import Markdown

from markdownextensions.tests.utils import MarkdownTestCase
from markdownextensions.metadata import MetaDataExtension


class TestMetaData(MarkdownTestCase):
    def test_should_find_metadata(self):
        metadata = MetaDataExtension()
        self.extensions = [metadata]
        markdowntext = (
            u"Foo: Bar\n"
            u"Baz: Qux Möp\n"
            u"\n"
            u"Hi!"
        )
        self.assertMDEquals(markdowntext,
                            u"<p>Hi!</p>")
        self.assertEquals(metadata.metadata,
                          {u'Foo': u'Bar',
                           u'Baz': u'Qux Möp'})
