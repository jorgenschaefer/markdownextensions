import urllib

from markdown.extensions import Extension
from markdown.util import etree
from markdown.treeprocessors import Treeprocessor


class COinSExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.treeprocessors.add('coins',
                              COinSProcessor(md_globals['metadataextension']),
                              '_end')


class COinSProcessor(Treeprocessor):
    def __init__(self, metadataextension, *args, **kwargs):
        Treeprocessor.__init__(self, *args, **kwargs)
        self.metadataextension = metadataextension

    def run(self, root):
        span = etree.SubElement(root, 'span')
        span.attrib['class'] = 'Z3988'
        titledata = [
            ('ctx_ver', 'Z39.88-2004'),
            ('rft_val_fmt', 'info:ofi/fmt:kev:mtx:dc'),
            ('rft.type', 'blogPost'),
            ('rft.format', 'text'),
        ]
        metadata = self.metadataextension.metadata
        if 'Author' in metadata:
            titledata.append(('rft.au', metadata['Author'].encode("utf-8")))
        if 'Title' in metadata:
            titledata.append(('rft.title', metadata['Title'].encode("utf-8")))
        if 'Date' in metadata:
            titledata.append(('rft.date', metadata['Date'].encode("utf-8")))
        span.attrib['title'] = urllib.urlencode(titledata)
        return root
