# coding: utf-8

"""Wikipedia-style citation extension.

You can use {{shortref, p. 33}} in the text to create [1] footnote
which links to the bibliography, with the full reference in a CSS
popup. It also creates an id'd tag for the reference so you can scroll
up here from the bibliography.

{{bibliography}} will insert a list of all used references, sorted by
publication year and author name, into the document, with links to the
referencing sections.

div#test:target can be used to reference the current target.

"""

import cgi
import os
import re
import urllib

from markdown.extensions import Extension
from markdown.inlinepatterns import Pattern
from markdown.treeprocessors import Treeprocessor
from markdown.util import etree, AtomicString


class CiteExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        self.citations = CitationList()
        md.inlinePatterns.add('cite', InlineCitations(self), "_end")
        # md.treeprocessors.add('cite', AddCSS(), '_begin')

    def reset(self):
        self.citations = CitationList()


class AddCSS(Treeprocessor):
    def run(self, root):
        style = etree.SubElement(root, "style")
        style.attrib["type"] = "text/css"
        style.text = AtomicString("""\
  .cite__footnote, .cite__backlink {
    font-size: 60%;
    top: -0.7em;
    position: relative;
  }

  span.cite__footnote:target {
    background: #DFDFFF;
  }

  ol#cite__bibliography li:target {
    background: #DFDFFF;
  }

  .cite__tooltip {
    display: none;
  }

  .cite__footnote:hover .cite__tooltip {
    font-size: 150%;
    display: block;
    position: absolute;
    left: 1em;
    top: 0.5em;
    z-index: 99;
    background: white;
    margin: 0;
    padding: 0.5em 1em;
    width: 30em;
    border: 1px solid #AAA;
  }
""")


class InlineCitations(Pattern):
    def __init__(self, extension):
        Pattern.__init__(self, "{{(.*?)}}")
        self.extension = extension

    def handleMatch(self, m):
        if m.group(2).lower() == 'bibliography':
            return self.bibliography()

        cit = self.extension.citations
        info = cit.use(m.group(2).replace("\n", " "))

        fn = etree.Element("span")
        fn.attrib["id"] = info["citeid"]
        fn.attrib["class"] = "cite__footnote"
        sp_open = etree.SubElement(fn, "span")
        sp_open.text = "["
        link = etree.SubElement(fn, "a")
        link.attrib["href"] = "#" + info["bibid"]
        link.text = str(info["fnnum"])
        sp_close = etree.SubElement(fn, "span")
        sp_close.text = "]"
        tooltip = etree.SubElement(fn, "span")
        tooltip.attrib["class"] = "cite__tooltip"
        tooltip.text = info["html"]

        return fn

    def bibliography(self):
        ol = etree.Element("ol")
        ol.attrib["id"] = "cite__bibliography"
        for cit in self.extension.citations.get_bibliography():
            li = etree.SubElement(ol, "li")
            li.attrib["id"] = cit["bibid"]
            li.attrib["value"] = cit["fnnum"]
            if len(cit["citeids"]) == 1:
                a = etree.SubElement(li, "a")
                a.attrib["href"] = "#" + cit["citeids"][0]
                a.text = "^"
                a.tail = " "
            else:
                caret = etree.SubElement(li, "span")
                caret.text = "^ "
                for citeid, name in zip(cit["citeids"],
                                        "abcdefghijklmnopqrstuvwxyz"):
                    a = etree.SubElement(li, "a")
                    a.attrib["href"] = "#" + citeid
                    a.attrib["class"] = "cite__backlink"
                    a.text = name
                    a.tail = " "
            text = etree.SubElement(li, "span")
            text.text = cit["html"]
        return ol


class CitationList(object):
    def __init__(self):
        self.known = None
        self.used = []
        self.next_fnnum = 1

    def use(self, reftext):
        """Mark a citation as used, and return appropriate info.

        reftext is something like "Mary 2004, p. 23".

        Return a dictionary with the following elements:

        fnnum: The number to use for the footnote.

        html: The full text of the citation, including the page
        reference.

        citeid: The HTML element id to use for the reference.

        bibid: The HTML element id to use to link to the
        bibliography entry.

        """
        cit = lookup(reftext, self.used)
        if cit:
            return cit.use(reftext)
        if self.known is None:
            self.load()
        cit = lookup(reftext, self.known)
        if cit:
            cit.set_fnnum(self.next_fnnum)
            self.next_fnnum += 1
            self.used.append(cit)
            return cit.use(reftext)
        raise RuntimeError("Unknown reference {}".format(repr(reftext)))

    def get_bibliography(self):
        """Return a list of bibliography entries.

        Each entry is a dictionary with the following fields:

        bibid: The HTML element id to use for this entry.

        citeids: A list of HTML element ids to link to from this
        element.

        html: The HTML-formatted text to use for the entry.

        """
        return [cit.bibentry() for cit in self.used]

    def load(self):
        with open(os.environ["BIBLIOGRAPHY"]) as f:
            self.known = [Citation(Entry(entry)) for entry
                          in wikipedia_parse(f.read().decode("utf-8"))]


class Citation(object):
    REFTEX_RX = re.compile("([^,0-9]+) ([0-9-]+)(?:, (.*))?")

    def __init__(self, entry):
        self.entry = entry
        self.fnnum = None
        self.next_citeid = 0
        self.citeids = []
        self.bibid = None
        self.html = entry.get_html()
        self.date = entry.date()
        self.authors = entry.authors()
        self.title = entry.title()

    def matches(self, reftext):
        if reftext == self.title:
            return True

        m = self.REFTEX_RX.match(reftext)
        if not m:
            return False

        authors = m.group(1)
        date = m.group(2)
        if authors == self.title:
            return True
        for author in re.findall(r"(\w+)", authors):
            if author not in self.authors:
                return False
        if self.date and date and date not in self.date:
            return False
        return True

    def set_fnnum(self, fnnum):
        assert self.fnnum is None
        self.fnnum = fnnum
        self.bibid = "ref{}".format(fnnum)

    def use(self, reftext):
        assert self.fnnum is not None
        assert self.bibid is not None
        citeid = "{bibid}-{citeid}".format(bibid=self.bibid,
                                           citeid=self.next_citeid)
        self.next_citeid += 1
        self.citeids.append(citeid)
        pages = self.extract_pages(reftext)
        if pages:
            html = self.html + " " + pages + "."
        else:
            html = self.html
        return {'fnnum': str(self.fnnum),
                'html': html,
                'citeid': citeid,
                'bibid': self.bibid}

    def bibentry(self):
        assert self.bibid is not None
        return {'fnnum': str(self.fnnum),
                'bibid': self.bibid,
                'citeids': self.citeids,
                'html': self.html}

    def extract_pages(self, reftext):
        m = self.REFTEX_RX.match(reftext)
        if m:
            return m.group(3)
        else:
            return None


class Entry(object):
    def __init__(self, data):
        self.data = data

    def get_html(self):
        authors = self.authors()
        date = self.date()
        title = self.title()
        work = self.work()
        volume = self.volume()
        issue = self.issue()
        pages = self.pages()
        doi = self.doi()
        issn = self.issn()
        accessdate = self.accessdate()
        url = self.url()

        html = []

        # $authors ($date). "$title". $work $volume ($issue): $pages.
        # doi:$doi, ISSN $issn. Retrieved $accessdate.

        if authors:
            html.append(cgi.escape(authors))
            if date:
                html.extend([" (", cgi.escape(date), ")"])
            html.append(". ")
        if url:
            html.extend(['<a href="', cgi.escape(url, quote=True), '">'])
        html.extend([u"<i>", cgi.escape(title), u"</i>"])
        if url:
            html.append('</a>')
        html.append(".")
        if work:
            html.extend([" ", cgi.escape(work)])
            if volume:
                html.extend([" ", cgi.escape(volume)])
            if issue:
                html.extend([" (", cgi.escape(issue), ")"])
            if pages:
                html.extend([": ", cgi.escape(pages)])
            html.append(".")
        if not authors and date:
            html.extend([" ", cgi.escape(date), "."])

        refs = []
        if doi:
            refs.append(u"".join([
                " ",
                ('<a href="http://en.wikipedia.org/wiki/'
                 'Digital_object_identifier">doi</a>:'),
                '<a href="http://dx.doi.org/',
                cgi.escape(urllib.quote(doi)),
                '">', cgi.escape(doi), '</a>']))
        if issn:
            refs.append(u"".join([
                " ",
                ('<a href="http://en.wikipedia.org/wiki/'
                 'International_Standard_Serial_Number">ISSN</a> '),
                '<a href="http://www.worldcat.org/issn/',
                cgi.escape(urllib.quote(issn)),
                '">', cgi.escape(issn), '</a>']))
        if refs:
            html.extend([", ".join(refs),
                         "."])

        if accessdate:
            html.extend([" Retrieved ", cgi.escape(accessdate), "."])

        return u"".join(html)

    def authors(self):
        author = self.data.get('author')
        authors = self.data.get('authors')
        coauthors = self.data.get('coauthors')
        first = self.data.get('first')
        last = self.data.get('last')
        others = self.data.get('others')
        result = []
        if author:
            result.append(author)
        if authors:
            result.append(authors)
        if coauthors:
            result.append(coauthors)
        if first or last:
            if first and not last:
                result.append(first)
            elif not first and last:
                result.append(last)
            else:
                result.append(first + " " + last)
        if others:
            result.append(others)
        return ", ".join(result)

    def date(self):
        return self.data.get("date")

    def title(self):
        return self.data["title"]

    def work(self):
        return (self.data.get('work') or
                self.data.get('journal') or
                self.data.get('newspaper') or
                self.data.get('magazine') or
                self.data.get('periodical') or
                self.data.get('encyclopedia'))

    def volume(self):
        return self.data.get('volume')

    def issue(self):
        return self.data.get('issue')

    def pages(self):
        return self.data.get('pages')

    def doi(self):
        return self.data.get("doi")

    def issn(self):
        return self.data.get("issn")

    def accessdate(self):
        return self.data.get("accessdate")

    def url(self):
        return self.data.get("url")


def wikipedia_parse(data):
    for bracelet in re.findall("{{(.*?)}}", data, re.DOTALL | re.MULTILINE):
        entry = {}
        row_list = bracelet.split("|")
        entry['macroname'] = row_list[0]
        for row in row_list[1:]:
            k, v = row.strip().split("=", 1)
            entry[k.strip().lower()] = v.strip()
        yield entry


def lookup(reftext, citlist):
    found = None
    for cit in citlist:
        if cit.matches(reftext):
            if found is not None:
                raise RuntimeError("Ambiguous reference {}"
                                   .format(repr(reftext)))
            found = cit
    return found
