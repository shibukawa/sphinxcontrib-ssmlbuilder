# -*- coding: utf-8 -*-
"""
    sphinxcontrib.ssmlbuilder
    =========================

    Sphinx extension to output SSML file for Amazon Polly

    .. moduleauthor:: Yoshiki Shibukawa <yoshiki@shibu.jp>

    :copyright: Copyright 2017- by Yoshiki Shibukawa.
    :license: BSD, see LICENSE.txt for details.
"""


from .builder import SSMLBuilder


def setup(app):
    app.require_sphinx('1.5')
    app.add_builder(SSMLBuilder)
    app.add_config_value('ssml_language', "en-US", True)
    app.add_config_value('ssml_break_around_section_title', [2000, 1600, 1000, 1000, 1000, 1000], True)
    app.add_config_value('ssml_emphasis_section_title', ['none', 'none', 'none', 'none', 'none', 'none'], True)
    app.add_config_value('ssml_skip_block', {'comment': True, 'table': True, 'codeblock': True}, True)
    app.add_config_value('ssml_paragraph_speed', 'default', True)
    app.add_config_value('ssml_break_after_paragraph', 1000, True)
    app.add_config_value('ssml_polly_audio_output_folder', "polly", True)
    app.add_config_value('ssml_polly_aws_profile', "", False)
    app.add_config_value('ssml_polly_aws_voiceid', "Joanna", True)
    app.add_config_value('ssml_polly_apply_docnames', "", False)
