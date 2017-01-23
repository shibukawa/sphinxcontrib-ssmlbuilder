# -*- coding: utf-8 -*-
"""
    sphinxcontrib.ssmlbuilder.writer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Custom docutils writer for SSML

    :copyright: Copyright 2017 by Yoshiki Shibukawa
    :license: BSD, see LICENSE for details.
"""

from docutils import nodes, writers, languages
from sphinx import addnodes
from xml.sax.saxutils import escape
import hashlib

class SSMLWriter(writers.Writer):
    supported = ('ssml',)

    def __init__(self, builder):
        # type: (TextBuilder) -> None
        writers.Writer.__init__(self)
        self.builder = builder
        self.translator_class = SSMLTranslator

    def write(self, document, destination, docname, basepath):
        self.document = document;
        self.language = languages.get_language(
                            document.settings.language_code,
                            document.reporter)
        self.translate(destination, docname, basepath)

    def translate(self, destination, docname, basepath):
        # type: () -> None
        visitor = self.translator_class(self.document, self.builder, destination, docname, basepath)
        self.document.walkabout(visitor)


def info(typ, node, *args):
    #if len(args) > 0:
    #    print(typ + "_" + node.tagname + ": " + "".join(args))
    #else:
    #    print(typ + "_" + node.tagname)
    pass


REGULAR = 0
JOIN_AFTER = 1
JOIN_BEFORE = 2


class SSMLTranslator(nodes.NodeVisitor):
    def __init__(self, document, builder, destination, docname, basepath):
        nodes.NodeVisitor.__init__(self, document)
        self.builder = builder
        self.sectionlevel = 0
        self.sectioncount = [0, 0, 0, 0, 0, 0]
        self.contents = [];  #[
        self.destination = destination
        self.docname = docname
        self.basepath = basepath
        self.state = ['regular']

    def active(self):
        laststate = self.state[-1]
        return not self.builder.ssml_skip_block.get(laststate, False)

    def add_text(self, text):
        # type: (unicode) -> None
        if self.active():
            self.contents.append([len(text), REGULAR, escape(text)])

    def reset_content(self):
        if len(self.contents) == 0:
            return
        # sentinel
        self.contents.append([0, REGULAR, ''])
        section_number = '.'.join([str(num) for num in self.sectioncount[1:self.sectionlevel]])
        character_count = 0
        outputs = []
        current_contents = []
        def next_node_character_count(index):
            while index < len(self.contents):
                content = self.contents[index]
                if content[0] > 0:
                    return content[0]
                index += 1
            return 0
        i = 0
        while i < len(self.contents) - 1:
            content = self.contents[i]
            character_count += content[0]
            if content[1] in (REGULAR, JOIN_AFTER):
                if character_count + next_node_character_count(i+1) > 900:
                    outputs.append(''.join(current_contents))
                    current_contents = []
                    character_count = content[0]
            current_contents.append(content[2])
            i += 1
        if len(current_contents) > 0:
            outputs.append(''.join(current_contents))
        for i, output in enumerate(outputs):
            middle = ''
            if section_number:
                middle = '.' + section_number
            if len(outputs) > 1:
                middle += "-" + str(i + 1)
            filepath = self.basepath + middle + ".ssml"
            filename = self.docname + middle + ".ssml"
            sha = hashlib.sha1(output.encode('utf-8')).hexdigest()
            self.destination["hashes"][sha] = filename
            self.destination["sequence"].append(sha)
            f = open(filepath, "w")
            #f.write('<?xml version="1.0"?>\n') 
            #f.write('''<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="%s">''' % self.builder.ssml_language)
            f.write('''<speak xml:lang="%s">''' % self.builder.ssml_language)
            if self.builder.ssml_paragraph_speed != 'medium':
                f.write('<prosody rate="%s">' % self.builder.ssml_paragraph_speed)
            f.write(output)
            if self.builder.ssml_paragraph_speed != 'medium':
                f.write('</prosody>')
            f.write('</speak>')
            f.close()
        self.contents = []

    def visit_document(self, node):
        info("visit", node)

    def depart_document(self, node):
        info("depart", node)

    def visit_highlightlang(self, node):
        raise nodes.SkipNode

    def visit_section(self, node):
        info("visit", node)
        self.sectioncount[self.sectionlevel] += 1
        self.reset_content()
        self.sectionlevel += 1

    def depart_section(self, node):
        info("depart", node)
        self.reset_content()
        self.sectionlevel -= 1

    def visit_topic(self, node):
        info("visit", node)

    def depart_topic(self, node):
        pass

    def visit_rubric(self, node):
        info("visit", node)

    def depart_rubric(self, node):
        pass

    def visit_compound(self, node):
        info("visit", node)

    def depart_compound(self, node):
        pass

    def visit_glossary(self, node):
        info("visit", node)

    def depart_glossary(self, node):
        pass

    def visit_title(self, node):
        if not self.destination['title']:
            self.destination['title'] = node.astext()
        level = self.sectionlevel-1
        breaklength = self.builder.ssml_break_around_section_title[level]
        emphasis = self.builder.ssml_emphasis_section_title[level]
        self.contents.append([0, JOIN_AFTER, '<break time="%dms" />' % breaklength])
        if emphasis != 'none':
            self.contents.append([0, JOIN_AFTER,  '<emphasis level="%s">' % emphasis])
        info("visit", node, str(level))

    def depart_title(self, node):
        level = self.sectionlevel-1
        breaklength = self.builder.ssml_break_around_section_title[level]
        emphasis = self.builder.ssml_emphasis_section_title[level]
        self.contents.append([0, JOIN_BEFORE, '<break time="%dms" />' % breaklength])
        if emphasis != 'none':
            self.contents.append([0, JOIN_BEFORE,  '</emphasis>'])
        info("depart", node, str(level))

    def visit_subtitle(self, node):
        info("visit", node)

    def depart_subtitle(self, node):
        info("depart", node)

    def visit_attribution(self, node):
        pass

    def depart_attribution(self, node):
        pass

    def visit_desc(self, node):
        pass

    def depart_desc(self, node):
        pass

    def visit_desc_signature(self, node):
        pass

    def depart_desc_signature(self, node):
        pass

    def visit_desc_signature_line(self, node):
        pass

    def depart_desc_signature_line(self, node):
        pass

    def visit_desc_name(self, node):
        pass

    def depart_desc_name(self, node):
        pass

    def visit_desc_addname(self, node):
        pass

    def depart_desc_addname(self, node):
        pass

    def visit_desc_type(self, node):
        pass

    def depart_desc_type(self, node):
        pass

    def visit_desc_returns(self, node):
        pass

    def depart_desc_returns(self, node):
        pass

    def visit_desc_parameterlist(self, node):
        pass

    def depart_desc_parameterlist(self, node):
        pass

    def visit_desc_parameter(self, node):
        pass

    def visit_desc_optional(self, node):
        pass

    def depart_desc_optional(self, node):
        pass

    def visit_desc_annotation(self, node):
        pass

    def depart_desc_annotation(self, node):
        pass

    def visit_desc_content(self, node):
        pass

    def depart_desc_content(self, node):
        pass

    def visit_figure(self, node):
        pass

    def depart_figure(self, node):
        pass

    def visit_caption(self, node):
        pass

    def depart_caption(self, node):
        pass

    def visit_productionlist(self, node):
        pass

    def visit_footnote(self, node):
        pass

    def depart_footnote(self, node):
        pass

    def visit_citation(self, node):
        pass

    def depart_citation(self, node):
        pass

    def visit_label(self, node):
        pass

    def visit_legend(self, node):
        pass

    def depart_legend(self, node):
        pass

    def visit_bullet_list(self, node):
        pass

    def depart_bullet_list(self, node):
        pass

    def visit_enumerated_list(self, node):
        pass

    def depart_enumerated_list(self, node):
        pass

    def visit_list_item(self, node):
        pass

    def depart_list_item(self, node):
        pass

    def visit_admonition(self, node):
        pass

    def depart_admonition(self, node):
        pass

    def _depart_admonition(self, node):
        pass

    def _make_visit_admonition(name):
        def visit_admonition(self, node):
            # type: (nodes.NodeVisitor, nodes.Node) -> None
            # self.end_state(first=admonitionlabels[name] + ': ')
            info("visit", node)
        return visit_admonition

    visit_attention = _make_visit_admonition('attention')
    depart_attention = _depart_admonition
    visit_caution = _make_visit_admonition('caution')
    depart_caution = _depart_admonition
    visit_danger = _make_visit_admonition('danger')
    depart_danger = _depart_admonition
    visit_error = _make_visit_admonition('error')
    depart_error = _depart_admonition
    visit_hint = _make_visit_admonition('hint')
    depart_hint = _depart_admonition
    visit_important = _make_visit_admonition('important')
    depart_important = _depart_admonition
    visit_note = _make_visit_admonition('note')
    depart_note = _depart_admonition
    visit_tip = _make_visit_admonition('tip')
    depart_tip = _depart_admonition
    visit_warning = _make_visit_admonition('warning')
    depart_warning = _depart_admonition
    visit_seealso = _make_visit_admonition('seealso')
    depart_seealso = _depart_admonition

    def visit_literal_block(self, node):
        pass

    def depart_literal_block(self, node):
        pass

    def depart_line_block(self, node):
        pass

    def visit_line_block(self, node):
        pass

    def visit_line(self, node):
        pass

    def depart_line(self, node):
        pass

    def visit_block_quote(self, node):
        info("visit", node)

    def depart_block_quote(self, node):
        info("depart", node)

    def visit_compact_paragraph(self, node):
        info("visit", node)

    def depart_compact_paragraph(self, node):
        info("depart", node)

    def visit_paragraph(self, node):
        # type: (nodes.Node) -> None
        if self.active():
            self.contents.append([0, JOIN_BEFORE, '<break time="%dms" />' % self.builder.ssml_break_after_paragraph])
        info("visit", node)

    def depart_paragraph(self, node):
        info("depart", node)

    def visit_Text(self, node):
        info("visit", node, node.astext())
        self.add_text(node.astext())

    def depart_Text(self, node):
        pass

    def visit_reference(self, node):
        info("visit", node)

    def depart_reference(self, node):
        info("depart", node)

    def visit_number_reference(self, node):
        info("visit", node)

    def depart_number_reference(self, node):
        info("depart", node)

    def visit_download_reference(self, node):
        pass

    def depart_download_reference(self, node):
        pass

    def visit_emphasis(self, node):
        info("visit", node)

    def depart_emphasis(self, node):
        info("depart", node)

    def visit_literal(self, node):
        info("visit", node)

    def depart_literal(self, node):
        info("depart", node)

    def visit_literal_emphasis(self, node):
        info("visit", node)

    def depart_literal_emphasis(self, node):
        info("depart", node)

    def visit_strong(self, node):
        info("visit", node)

    def depart_strong(self, node):
        info("depart", node)

    def visit_literal_strong(self, node):
        info("visit", node)

    def depart_literal_strong(self, node):
        info("depart", node)

    def visit_target(self, node):
        info("visit", node)

    def depart_target(self, node):
        info("depart", node)

    def visit_inline(self, node):
        info("visit", node)

    def depart_inline(self, node):
        info("depart", node)

    def visit_index(self, node):
        info("visit", node)

    def depart_index(self, node):
        info("depart", node)

    def visit_label(self, node):
        info("visit", node)

    def depart_label(self, node):
        info("depart", node)

    def visit_footnote_reference(self, node):
        info("visit", node)

    def depart_footnote_reference(self, node):
        info("depart", node)

    def visit_table(self, node):
        self.state.append('table')
        info("visit", node)

    def depart_table(self, node):
        self.state.pop()
        info("depart", node)

    def visit_tgroup(self, node):
        info("visit", node)

    def depart_tgroup(self, node):
        info("depart", node)

    def visit_colspec(self, node):
        info("visit", node)

    def depart_colspec(self, node):
        info("depart", node)

    def visit_thead(self, node):
        info("visit", node)

    def depart_thead(self, node):
        info("depart", node)

    def visit_tbody(self, node):
        info("visit", node)

    def depart_tbody(self, node):
        info("depart", node)

    def visit_row(self, node):
        info("visit", node)

    def depart_row(self, node):
        info("depart", node)

    def visit_entry(self, node):
        info("visit", node)

    def depart_entry(self, node):
        info("depart", node)

    def visit_definition_list(self, node):
        info("visit", node)

    def depart_definition_list(self, node):
        info("depart", node)

    def visit_definition_list_item(self, node):
        info("visit", node)

    def depart_definition_list_item(self, node):
        info("depart", node)

    def visit_term(self, node):
        info("visit", node)

    def depart_term(self, node):
        info("depart", node)

    def visit_definition(self, node):
        info("visit", node)

    def depart_definition(self, node):
        info("depart", node)

    def visit_image(self, node):
        info("visit", node)

    def depart_image(self, node):
        info("depart", node)

    def visit_todo_node(self, node):
        info("visit", node)

    def depart_todo_node(self, node):
        info("depart", node)

    def visit_problematic(self, node):
        info("visit", node)

    def depart_problematic(self, node):
        info("depart", node)

    def visit_container(self, node):
        self.state.append('codeblock')
        info("visit", node)

    def depart_container(self, node):
        self.state.pop()
        info("depart", node)

    def visit_comment(self, node):
        self.state.append('comment')
        info("visit", node)

    def depart_comment(self, node):
        self.state.pop()
        info("depart", node)

    def visit_title_reference(self, node):
        info("visit", node)

    def depart_title_reference(self, node):
        info("depart", node)

    def visit_transition(self, node):
        info("visit", node)

    def depart_transition(self, node):
        info("depart", node)
