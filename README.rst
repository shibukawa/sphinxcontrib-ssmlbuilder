sphinxcontrib-ssmlbuilder
=========================

It is a Sphinx's builder to generate MP3 files from reST files by using `Amazon Polly <https://aws.amazon.com/polly/>`_.

* It can generate SSML format files.
* It kicks Amazon Polly and get MP3 fragments.
* Finally it kicks ffmpeg to concat MP3 fragments into one MP3 file.

Amazon Polly API has text size limitation (1000 chracters without SSML tags). This builder generates small valid size SSML files for Polly.
It caches MP3 fragments to reduce API access (it keeps hashes and reuse it).

Requirement
------------

* boto3, awscli (see last note at : http://docs.aws.amazon.com/polly/latest/dg/examples-python.html)
* AWS IAM user (that has Polly read access right. Few regions support Polly.)
* ffmpeg

`Getting Started with Amazon Polly <http://docs.aws.amazon.com/polly/latest/dg/getting-started.html>`_ is a good entry point to setup.

Usage
------

.. code-block:: bash

   pip install sphinxcontrib-ssmlbuilder

Add setting like this:

.. code-block:: python

   extensions = ['sphinxcontrib.ssmlbuilder']
   # you should register the following user name
   # via aws configure.
   ssml_polly_aws_profile = "polly_user"
   ssml_polly_apply_docnames = "*"

   # for Japanese
   ssml_language = 'ja-JP'
   ssml_polly_aws_voiceid = 'Mizuki'
   
Setting
-------

.. list-table:: sphinxcontrib-ssmlbuilder configuration
   :header-rows: 1

   - * Config Key
     * Default Value
     * Description
     * Available values
   - * ``ssml_language``
     * ``"en-US"``
     * SSML speaking language option.
     * `AWS Doc <http://docs.aws.amazon.com/polly/latest/dg/API_Voice.html#polly-Type-Voice-LanguageCode>`_
   - * ``ssml_skip_block``
     * ``{'comment': True, 'table': True, 'codeblock': True}``
     * If the value is True, the content inside the blocks are omitted from resulting SSML.
     *
   - * ``ssml_break_around_section_title``
     * ``[2000, 1600, 1000, 1000, 1000, 1000]``
     * Break time (millisecond) around section title.
     *
   - * ``ssml_emphasis_section_title``
     * ``['none', 'none', 'none', 'none', 'none', 'none']``
     * Emphasis level of section titles
     * ``"strong"``, ``"moderate"``, ``"none"``, ``"reduced"``
   - * ``ssml_paragraph_speed``
     * ``"default"``
     * Speech speed
     * ``"x-slow"``, ``"slow"``, ``"medium"``, ``"fast"``, ``"x-fast"``, ``"default"``
   - * ``ssml_break_after_paragraph``
     * ``1000``
     * Break time after paragraph (millisecond).
     *
   - * ``ssml_polly_audio_output_folder``
     * ``polly``
     * Output folder for resulting files. It uses outside of build folder to avoid ``make clean`` to save money.
     *
   - * ``ssml_polly_aws_profile``
     * ``''``
     * AWS Profile name that is configured by ``aws configure`` command.
     *
   - * ``ssml_polly_aws_voice_id``
     * ``"Joanna"``
     * Voice ID to use for the Polly synthesis.
     * `AWS Doc <http://docs.aws.amazon.com/polly/latest/dg/API_SynthesizeSpeech.html#polly-SynthesizeSpeech-request-VoiceId>`_
   - * ``ssml_polly_apply_docnames``
     * ``''``
     * Docname pattern you want to adopt Polly.
       If you want to convert only "readme.rst" on top folder, set ``"readme"``.
       ``"*"`` matches all document.
       Default value doesn't match with any files.
     *

License
-------

BSD License

Author
------

Yoshiki Shibukawa

Repository
-----------

https://github.com/shibukawa/sphinxcontrib-ssmlbuilder

History
-------

* 0.1.2 Jan 24 2017

  * Change default speed to ``default``
  * Remove duplicated breaks after paragraphs
  * Add metadata to resulting MP3 (title, author, track, year, genre)

* 0.1.1 Jan 23 2017

  * Add skipping block option

* 0.1 Jan 23 2017

  * Initial Version

