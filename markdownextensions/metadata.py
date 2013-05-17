import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor


class MetaDataExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        self.metadata = {}
        md_globals['metadataextension'] = self
        md.registerExtension(self)
        md.preprocessors.add('metadata',
                             MetaDataParser(self),
                             '_begin')

    def reset(self):
        self.metadata = {}


class MetaDataParser(Preprocessor):
    def __init__(self, extension, *args, **kwargs):
        Preprocessor.__init__(self, *args, **kwargs)
        self.extension = extension

    def run(self, lines):
        while lines:
            if lines[0].strip() == '':
                lines.pop(0)
                break
            m = re.match("^([A-Za-z0-9_-]+): *(.*) *$",
                         lines[0])
            if m is None:
                break
            self.extension.metadata[m.group(1)] = m.group(2)
            lines.pop(0)
        return lines
