import sys
from xml.etree import ElementTree

import lxml.etree
import cssutils
import cssselect


def _translate_stylesheet(stylesheet, translator):
    for rule in stylesheet.cssRules:
        # If is an import rule, the generator is going to be recursive!
        if isinstance(rule, cssutils.css.CSSImportRule):
            for trans_rule in \
              _translate_stylesheet(rule.styleSheet, translator):
                yield trans_rule
        elif isinstance(rule, cssutils.css.CSSStyleRule):
            selector = rule.selectorText
            xsel = translator.css_to_xpath(selector)
            yield (xsel, {prop.name: prop.value
                          for prop in rule.style.getProperties()})


def _apply_css_sheets(xmlstring, *sheets):
    tree = lxml.etree.fromstring(xmlstring)
    final_rules = translate_css_to_xpath(*sheets)
    for (xsel, attribs) in final_rules:
        for elem in tree.xpath(xsel):
            for name, value in attribs.items():
                elem.attrib[name] = value
    # After the styles related to the class has been inlined,
    # remove the class attribute to be a valid FO.
    for elem_with_class in tree.xpath('descendant-or-self::*[@class]'):
        del elem_with_class.attrib['class']
    return lxml.etree.tostring(tree)


def _fofactory(tag, attribs):
    """
    Factory to create each element with the fo: namespace.
    """
    return ElementTree.Element(_foname(tag), attribs)


def _foname(tag):
    """Append the fo: namespace to the tag.
    If the tag already have a namespace return the tag unmodified.
    """
    if ':' in tag:
        return tag
    # if no namespace is specified use 'fo'.
    return 'fo:{}'.format(tag)


def translate_css_to_xpath(*sheets):
    gtrans = cssselect.GenericTranslator()
    xpath_n_styles = []  # using a list, to be hable to "cascade".
    for sheet_path in sheets:
        stylesheet = cssutils.parseFile(sheet_path)
        xpath_n_styles.extend(_translate_stylesheet(stylesheet, gtrans))
    return xpath_n_styles


def translate_to_fo(xmlstring, encoding):
    """Add the fo: namespace to all the objects in the xml."""
    builder = FOBuilder(_fofactory)
    fop_parser_creator = ElementTree.XMLParser(target=builder)
    fop_parser_creator.feed(xmlstring)
    foroot = fop_parser_creator.close()
    foroot.attrib['xmlns:fo'] = 'http://www.w3.org/1999/XSL/Format'
    if encoding is None:
        encoding = sys.getdefaultencoding()
    doctype = '<?xml version="1.1" encoding="%s"?>\n' % encoding
    return b''.join((doctype.encode(encoding), ElementTree.tostring(foroot)))


def xml_to_fo_with_style(xmlstring, csssheets, encoding=None):
    if csssheets is not None:
        if isinstance(csssheets, str):
            xmlstring = _apply_css_sheets(xmlstring, csssheets)
        else:  # asume it is an iterator with sheets.
            xmlstring = _apply_css_sheets(xmlstring, *csssheets)
    return translate_to_fo(xmlstring, encoding)


class FOBuilder(ElementTree.TreeBuilder):

    def end(self, tag):
        ElementTree.TreeBuilder.end(self, _foname(tag))
