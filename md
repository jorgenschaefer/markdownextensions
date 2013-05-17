#!/usr/bin/env python

import sys

import markdown

from markdownextensions.codeblocks import CodeBlockExtension
from markdownextensions.metadata import MetaDataExtension
from markdownextensions.coins import COinSExtension
from markdownextensions.cite import CiteExtension


def main():
    if len(sys.argv) != 2:
        exit("usage: bmd <file.md>")

    data = open(sys.argv[1]).read().decode("utf-8")
    metadata = {}
    md = markdown.Markdown(extensions=[
        CodeBlockExtension(),
        MetaDataExtension(metadata),
        COinSExtension(metadata),
        CiteExtension(metadata),
    ])
    print md.convert(data).encode("utf-8")


main()
