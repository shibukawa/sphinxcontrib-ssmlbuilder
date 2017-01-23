
# -*- coding: utf-8 -*-
"""
    sphinxcontrib.ssmlbuilder
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    SSML Sphinx builder.

    :copyright: Copyright 2017- by Yoshiki Shibukawa.
    :license: BSD, see LICENSE.txt for details.
"""

from docutils.io import StringOutput
from sphinx.builders import Builder
from .writer import SSMLWriter
from sphinx.util.osutil import SEP, os_path, relative_uri, ensuredir, \
    movefile, copyfile
from sphinx import addnodes
import os
from os import path
import codecs
import json
import subprocess
from fnmatch import fnmatch
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
import datetime
import re


class SSMLBuilder(Builder):
    name = 'ssml'
    format = 'ssml'
    file_suffix = '.ssml'
    file_list_suffix = '.json'
    copysource = False
    allow_parallel = True
    ssml_language = 'en-US'
    ssml_skip_block = {'comment': True, 'table': True, 'codeblock': True}
    ssml_break_around_section_title = [2000, 1600, 1000, 1000, 1000, 1000]
    ssml_break_after_paragraph = 1000
    ssml_emphasis_section_title = ['none', 'none', 'none', 'none', 'none', 'none']
    ssml_paragraph_speed = 'default'
    ssml_polly_audio_output_folder = 'polly'
    ssml_polly_aws_profile = ''
    ssml_polly_aws_voiceid = 'Joanna'
    ssml_polly_apply_docnames = ''

    def init(self):
        """Load necessary templates and perform initialization."""
        if self.config.ssml_language is not None:
            self.ssml_language = self.config.ssml_language
        if self.config.ssml_skip_block is not None:
            self.ssml_skip_block = self.config.ssml_skip_block
        if self.config.ssml_break_around_section_title is not None:
            self.ssml_break_around_section_title = self.config.ssml_break_around_section_title
        if self.config.ssml_break_after_paragraph is not None:
            self.ssml_break_after_paragraph = self.config.ssml_break_after_paragraph
        if self.config.ssml_emphasis_section_title is not None:
            self.ssml_emphasis_section_title = self.config.ssml_emphasis_section_title
        if self.config.ssml_paragraph_speed is not None:
            self.ssml_paragraph_speed = self.config.ssml_paragraph_speed
        if self.config.ssml_polly_audio_output_folder is not None:
            self.ssml_polly_audio_output_folder = self.config.ssml_polly_audio_output_folder
        if self.config.ssml_polly_aws_profile is not None:
            self.ssml_polly_aws_profile = self.config.ssml_polly_aws_profile
        if self.config.ssml_polly_aws_voiceid is not None:
            self.ssml_polly_aws_voiceid = self.config.ssml_polly_aws_voiceid
        
        def run_exec_polly(app, exception):
            self.exec_polly()
        self.app.connect("build-finished", run_exec_polly)

    def file_transform(self, docname):
        return docname + self.file_list_suffix

    def get_outdated_docs(self):
        for docname in self.env.found_docs:
            if docname not in self.env.all_docs:
                yield docname
                continue
            targetname = path.join(self.outdir, self.file_transform(docname))
            try:
                targetmtime = path.getmtime(targetname)
            except Exception:
                targetmtime = 0
            try:
                srcmtime = path.getmtime(self.env.doc2path(docname))
                if srcmtime > targetmtime:
                    yield docname
            except EnvironmentError:
                # source doesn't exist anymore
                pass

    def get_target_uri(self, docname, typ=None):
        return ''

    def prepare_writing(self, docnames):
        self.writer = SSMLWriter(self)

    def write_doc(self, docname, doctree):
        destination = {"hashes": {}, "sequence": [], "title": ""}
        outfilename = path.join(self.outdir, self.file_transform(docname))
        ensuredir(path.dirname(outfilename))
        self.writer.write(doctree, destination, docname, path.join(self.outdir, docname))
        try:
            f = codecs.open(outfilename, 'w', 'utf-8')
            try:
                json.dump(destination, f)
            finally:
                f.close()
        except (IOError, OSError) as err:
            self.warn("error writing file %s: %s" % (outfilename, err))

    def sort_docnames(self):
        result = [self.config.master_doc]
        self._sort_docnames(self.config.master_doc, result)
        return result

    def _sort_docnames(self, docname, traversed):
        tree = self.env.get_doctree(docname)
        for toctreenode in tree.traverse(addnodes.toctree):
            includefiles = map(str, toctreenode['includefiles'])
            for includefile in includefiles:
                 if includefile not in traversed:
                     try:
                         traversed.append(includefile)
                         self._sort_docnames(includefile, traversed)
                     except Exception:
                         pass

    def exec_polly(self):
        print("ssml_polly_aws_profile: ", self.ssml_polly_aws_profile)
        print("ssml_polly_apply_docnames: ", self.config.ssml_polly_apply_docnames)
        print("audio output folder: ", self.ssml_polly_audio_output_folder)
        print("ssml_polly_aws_voiceid: ", self.ssml_polly_aws_voiceid)

        # config path
        apply_docname = self.config.ssml_polly_apply_docnames
    
        # workpath
        outputpath = path.join(path.abspath("."), self.ssml_polly_audio_output_folder)
        workdirpath = path.join(outputpath, "_temp")
        ensuredir(workdirpath)
    
        # read_config
        allhash = set()
        hash2path = {}
        allneededhash = set()
        targets = []
        for docname in self.env.found_docs:
            setting = path.join(self.outdir, self.file_transform(docname))
            f = open(setting)
            d = json.load(f)
            for hashname in d["hashes"]:
                allhash.add(hashname)
            hash2path.update(d["hashes"])
            if fnmatch(docname, apply_docname):
                targets.append({"docname": docname, "sequence": d["sequence"], "title": d["title"]})
                for hashname in d["hashes"]:
                    allneededhash.add(hashname)
        # read existing path
        existinghash = set()
        for mp3file in os.listdir(workdirpath):
            hashpart, ext = path.splitext(mp3file)
            if ext == '.mp3':
                existinghash.add(hashpart)
        must_remove = existinghash - allhash
        must_convert = allneededhash - existinghash
        #print("targets", targets)
        #print("must_remove:", must_remove)
        #print("must_convert:", must_convert)

        # exec polly
        session = Session(profile_name=self.ssml_polly_aws_profile)
        polly = session.client("polly")
        task = 1 
        for hashkey in must_convert:
            print(f"polly.synthesize_speech for {hash2path[hashkey]} ({task}/{len(must_convert)})")
            task+=1
            ssmlpath = path.join(self.outdir, hash2path[hashkey])
            ssmlsource = open(ssmlpath).read()
            try:
                # Request speech synthesis
                response = polly.synthesize_speech(Text=ssmlsource,
                                                   VoiceId=self.ssml_polly_aws_voiceid,
                                                   TextType='ssml',
                                                   OutputFormat="mp3")
            except (BotoCoreError, ClientError) as err:
                # The service returned an error
                raise HTTPStatusError(HTTP_STATUS["INTERNAL_SERVER_ERROR"],
                                      str(err))

            mp3file = open(path.join(workdirpath, f"{hashkey}.mp3"), "wb")
            mp3file.write(response.get("AudioStream").read())
            mp3file.close()

        # metadata
        album = self.config.project
        year = datetime.datetime.now().year
        author = ''
        match = re.match(r'(\d{4}), (.*)', self.config.copyright)
        if match:
            year = match.group(1)
            author = match.group(2)
        document_order = self.sort_docnames()

        # concat mp3 fragments
        task = 1 
        for target in targets:
            docname = target['docname']
            title = target['title']
            track = document_order.index(docname) + 1

            print(f"concatinating MP3 fragments: {docname}.mp3 ({task}/{len(targets)})")
            task+=1
            sources = [hashkey + '.mp3' for hashkey in target['sequence']]
            outfilename = path.join(outputpath, f"{docname}.mp3")
            ensuredir(path.dirname(outfilename))

            args = ['ffmpeg', "-y", "-i", "concat:" + "|".join(sources), "-c", "copy",
                    '-metadata', f'album={album}',
                    '-metadata', f'author={author}',
                    '-metadata', f'title={title}',
                    '-metadata', f'track={track}',
                    '-metadata', 'genre=Audio Book',
                    '-metadata', f'year={year}',
                    outfilename]
            #print(args, workdirpath)
            p = subprocess.Popen(args, shell=False, cwd=workdirpath)
            p.wait()

        # remove unused file
        for hashkey in must_remove:
            os.remove(path.join(workdirpath, hashkey + '.mp3'))
