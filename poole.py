#!/usr/bin/python2
# -*- coding: utf-8 -*-

# =============================================================================
#
#    Poole - A damn simple static website generator.
#    Copyright (C) 2012 Oben Sonne <obensonne@googlemail.com>
#
#    This file is part of Poole.
#
#    Poole is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Poole is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Poole.  If not, see <http://www.gnu.org/licenses/>.
#
# =============================================================================

import codecs
import glob
import imp
import optparse
import os
from os.path import join as opj
from os.path import exists as opx
import re
import shutil
import StringIO
import sys
import traceback
import urlparse

from SimpleHTTPServer import SimpleHTTPRequestHandler
from BaseHTTPServer import HTTPServer

import markdown

HERE = os.path.dirname(os.path.realpath(__file__))

THEME_DIR = opj(HERE, 'themes')

THEME_NAMES = ['minimal'] + [
    os.path.basename(x)
    for x in glob.glob(opj(THEME_DIR, '*'))
    if os.path.isdir(x)
]

# =============================================================================
# build site
# =============================================================================

MKD_PATT = r'\.(?:md|mkd|mdown|markdown)$'

def hx(s):
    """
    Replace the characters that are special within HTML (&, <, > and ")
    with their equivalent character entity (e.g., &amp;). This should be
    called whenever an arbitrary string is inserted into HTML (so in most
    places where you use {{ variable }} in your templates).

    Note that " is not special in most HTML, only within attributes.
    However, since escaping it does not hurt within normal HTML, it is
    just escaped unconditionally.
    """
    if getattr(s, 'escaped', False):
        return s

    escape = {
        "&": "&amp;",
        '"': "&quot;",
        ">": "&gt;",
        "<": "&lt;",
    }
    return ''.join(escape.get(c, c) for c in s)

class Page(dict):
    """Abstraction of a source page."""

    _template = None # template dictionary
    _opts = None # command line options
    _pstrip = None # path prefix to strip from (non-virtual) page file names

    _re_eom = re.compile(r'^---+ *\r?\n?$')
    _re_vardef = re.compile(r'^([^\n:=]+?)[:=]((?:.|\n )*)', re.MULTILINE)
    _sec_macros = "macros"
    _modmacs = None

    def __init__(self, fname, virtual=None, **attrs):
        """Create a new page.

        Page content is read from `fname`, except when `virtual` is given (a
        string representing the raw content of a virtual page).

        The filename refers to the page source file. For virtual pages, this
        *must* be relative to a projects input directory.

        Virtual pages may contain page attribute definitions similar to real
        pages. However, it probably is easier to provide the attributes
        directly. This may be done using arbitrary keyword arguments.

        """
        super(Page, self).__init__()

        self.update(self._template)
        self.update(attrs)

        self._virtual = virtual is not None

        fname = opj(self._pstrip, fname) if virtual else fname

        self["fname"] = fname

        self["url"] = re.sub(MKD_PATT, ".html", fname)
        self["url"] = self["url"][len(self._pstrip):].lstrip(os.path.sep)
        self["url"] = self["url"].replace(os.path.sep, "/")

        if virtual:
            self.raw = virtual
        else:
            with codecs.open(fname, 'r', self._opts.input_enc) as fp:
                self.raw = fp.readlines()

        # split raw content into macro definitions and real content
        vardefs = ""
        self.source = ""
        for line in self.raw:
            if not vardefs and self._re_eom.match(line):
                vardefs = self.source
                self.source = "" # only macro defs until here, reset source
            else:
                self.source += line

        for key, val in self._re_vardef.findall(vardefs):
            key = key.strip()
            val = val.strip()
            val = re.sub(r' *\n +', ' ', val) # clean out line continuation
            self[key] = val

        basename = os.path.basename(fname)

        fpatt = r'(.+?)(?:\.([0-9]+-[0-9]+-[0-9]+)(?:\.(.*))?)?%s' % MKD_PATT
        title, date, post = re.match(fpatt, basename).groups()
        title = title.replace("_", " ")
        post = post and post.replace("_", " ") or None
        self["title"] = self.get("title", title)
        if date and "date" not in self: self["date"] = date
        if post and "post" not in self: self["post"] = post

        self.html = ""

    def __getattr__(self, name):
        """Attribute-style access to dictionary items."""
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __str__(self):
        """Page representation by file name."""
        return ('%s (virtual)' % self.fname) if self._virtual else self.fname

# -----------------------------------------------------------------------------

def build(project, opts):
    """Build a site project."""

    # -------------------------------------------------------------------------
    # utilities
    # -------------------------------------------------------------------------

    def abort_iex(page, itype, inline, exc):
        """Abort because of an exception in inlined Python code."""
        print("abort  : Python %s in %s failed" % (itype, page))
        print((" %s raising the exception " % itype).center(79, "-"))
        print(inline)
        print(" exception ".center(79, "-"))
        print(exc)
        sys.exit(1)

    # -------------------------------------------------------------------------
    # regex patterns and replacements
    # -------------------------------------------------------------------------

    regx_escp = re.compile(r'\\((?:(?:&lt;|<)!--|{)(?:{|%))') # escaped code
    repl_escp = r'\1'
    regx_rurl = re.compile(r'(?<=(?:(?:\n| )src|href)=")([^#/&%].*?)(?=")')
    repl_rurl = lambda m: urlparse.urljoin(opts.base_url, m.group(1))

    regx_eval = re.compile(r'(?<!\\)(?:(?:<!--|{){)(.*?)(?:}(?:-->|}))', re.S)

    def repl_eval(m):
        """Replace a Python expression block by its evaluation."""

        expr = m.group(1)
        try:
            repl = eval(expr, macros.copy())
        except:
            abort_iex(page, "expression", expr, traceback.format_exc())
        else:
            if not isinstance(repl, basestring): # e.g. numbers
                repl = unicode(repl)
            elif not isinstance(repl, unicode):
                repl = repl.decode("utf-8")
            return repl

    regx_exec = re.compile(r'(?<!\\)(?:(?:<!--|{)%)(.*?)(?:%(?:-->|}))', re.S)

    def repl_exec(m):
        """Replace a block of Python statements by their standard output."""

        stmt = m.group(1).replace("\r\n", "\n")

        # base indentation
        ind_lvl = len(re.findall(r'^(?: *\n)*( *)', stmt, re.MULTILINE)[0])
        ind_rex = re.compile(r'^ {0,%d}' % ind_lvl, re.MULTILINE)
        stmt = ind_rex.sub('', stmt)

        # execute
        sys.stdout = StringIO.StringIO()
        try:
            exec stmt in macros.copy()
        except:
            sys.stdout = sys.__stdout__
            abort_iex(page, "statements", stmt, traceback.format_exc())
        else:
            repl = sys.stdout.getvalue()[:-1] # remove last line break
            sys.stdout = sys.__stdout__
            if not isinstance(repl, unicode):
                repl = repl.decode(opts.input_enc)
            return repl

    # -------------------------------------------------------------------------
    # preparations
    # -------------------------------------------------------------------------

    dir_in = opj(project, "input")
    dir_out = opj(project, "output")
    page_html = opj(project, "page.html")

    # check required files and folders
    for pelem in (page_html, dir_in, dir_out):
        if not opx(pelem):
            print("abort  : %s does not exist, looks like project has not been "
                  "initialized" % pelem)
            sys.exit(1)

    # prepare output directory
    if not opts.dry_run:
        for fod in glob.glob(opj(dir_out, "*")):
            if os.path.isdir(fod):
                shutil.rmtree(fod)
            else:
                os.remove(fod)
        if not opx(dir_out):
            os.mkdir(dir_out)

    # macro module
    fname = opj(opts.project, "macros.py")
    macros = imp.load_source("macros", fname).__dict__ if opx(fname) else {}

    macros["__encoding__"] = opts.output_enc
    macros["options"] = opts
    macros["project"] = project
    macros["input"] = dir_in
    macros["output"] = dir_out

    # "builtin" items for use in macros and templates
    macros["hx"] = hx
    macros["htmlspecialchars"] = hx # legacy name of `htmlx` function
    macros["Page"] = Page

    # -------------------------------------------------------------------------
    # process input files
    # -------------------------------------------------------------------------

    Page._template = macros.get("page", {})
    Page._opts = opts
    Page._pstrip = dir_in
    pages = []
    custom_converter = macros.get('converter', {})

    for cwd, dirs, files in os.walk(dir_in.decode(opts.filename_enc)):
        cwd_site = cwd[len(dir_in):].lstrip(os.path.sep)
        if not opts.dry_run:
            for sdir in dirs[:]:
                if re.search(opts.ignore, opj(cwd_site, sdir)):
                    dirs.remove(sdir)
                else:
                    os.mkdir(opj(dir_out, cwd_site, sdir))
        for f in files:
            if re.search(opts.ignore, opj(cwd_site, f)):
                pass
            elif re.search(MKD_PATT, f):
                page = Page(opj(cwd, f))
                pages.append(page)
            else:
                # either use a custom converter or do a plain copy
                for patt, (func, ext) in custom_converter.items():
                    if re.search(patt, f):
                        f_src = opj(cwd, f)
                        f_dst = opj(dir_out, cwd_site, f)
                        f_dst = '%s.%s' % (os.path.splitext(f_dst)[0], ext)
                        print('info   : convert %s (%s)' %
                            (f_src, func.__name__))
                        if not opts.dry_run:
                            func(f_src, f_dst)
                        break
                else:
                    if not opts.dry_run:
                        src = opj(cwd, f)
                        try:
                            shutil.copy(src, opj(dir_out, cwd_site))
                        except OSError:
                            # some filesystems like FAT won't allow shutil.copy
                            shutil.copyfile(src, opj(dir_out, cwd_site, f))

    pages.sort(key=lambda p: int(p.get("sval", "0")))

    macros["pages"] = pages

    # -------------------------------------------------------------------------
    # run pre-convert hooks in macro module (named 'once' before)
    # -------------------------------------------------------------------------

    hooks = [a for a in macros if re.match(r'hook_preconvert_|once_', a)]
    for fn in sorted(hooks):
        macros[fn]()

    # -------------------------------------------------------------------------
    # convert pages (markdown to HTML)
    # -------------------------------------------------------------------------

    for page in pages:

        print("info   : convert %s" % page)

        # replace expressions and statements in page source
        macros["page"] = page
        out = regx_eval.sub(repl_eval, page.source)
        out = regx_exec.sub(repl_exec, out)

        # convert to HTML
        page.html = markdown.Markdown(extensions=opts.md_ext).convert(out)

    # -------------------------------------------------------------------------
    # run post-convert hooks in macro module
    # -------------------------------------------------------------------------

    hooks = [a for a in macros if a.startswith("hook_postconvert_")]
    for fn in sorted(hooks):
        macros[fn]()

    # -------------------------------------------------------------------------
    # render complete HTML pages
    # -------------------------------------------------------------------------

    with codecs.open(opj(project, "page.html"), 'r', opts.input_enc) as fp:
        default_template = fp.read()

    for page in pages:

        if 'template' in page:
            fname = opj(project, page['template'])
            with codecs.open(fname, 'r', opts.input_enc) as fp:
                template = fp.read()
        else:
            template = default_template

        print("info   : render %s" % page.url)

        # replace expressions and statements in page.html
        macros["page"] = page
        macros["__content__"] = page.html
        out = regx_eval.sub(repl_eval, template)
        out = regx_exec.sub(repl_exec, out)

        # un-escape escaped python code blocks
        out = regx_escp.sub(repl_escp, out)

        # make relative links absolute
        out = regx_rurl.sub(repl_rurl, out)

        # write HTML page
        fname = page.fname.replace(dir_in, dir_out)
        fname = re.sub(MKD_PATT, ".html", fname)
        if not opts.dry_run:
            with codecs.open(fname, 'w', opts.output_enc) as fp:
                fp.write(out)

    if opts.dry_run:
        print("success: built project (dry-run)")
    else:
        print("success: built project")

# =============================================================================
# serve site
# =============================================================================

def serve(project, port):
    """Temporary serve a site project."""

    root = opj(project, "output")
    if not os.listdir(project):
        print("abort  : output dir is empty (build project first!)")
        sys.exit(1)

    os.chdir(root)
    server = HTTPServer(('', port), SimpleHTTPRequestHandler)
    server.serve_forever()

# =============================================================================
# options
# =============================================================================

def options():
    """Parse and validate command line arguments."""

    usage = ("Usage: %prog --build [OPTIONS] [path/to/project]\n"
             "       %prog --serve [OPTIONS] [path/to/project]\n"
             "\n"
             "       Project path is optional, '.' is used as default.")

    op = optparse.OptionParser(usage=usage)

    op.add_option("-b" , "--build", action="store_true", default=False,
                  help="build project")
    op.add_option("-s" , "--serve", action="store_true", default=False,
                  help="serve project")


    og = optparse.OptionGroup(op, "Build options")
    og.add_option("", "--base-url", default="/", metavar="URL",
                  help="base url for relative links (default: /)")
    og.add_option("" , "--ignore", default=r"^\.|~$", metavar="REGEX",
                  help="input files to ignore (default: '^\.|~$')")
    og.add_option("" , "--md-ext", default=[], metavar="EXT",
                  action="append", help="enable a markdown extension")
    og.add_option("", "--input-enc", default="utf-8", metavar="ENC",
                  help="encoding of input pages (default: utf-8)")
    og.add_option("", "--output-enc", default="utf-8", metavar="ENC",
                  help="encoding of output pages (default: utf-8)")
    og.add_option("", "--filename-enc", default="utf-8", metavar="ENC",
                  help="encoding of file names (default: utf-8)")
    og.add_option("" , "--dry-run", action="store_true", default=False,
                  help="go through the rendering process without actually "
                    "outputting/deleting any files")
    op.add_option_group(og)

    og = optparse.OptionGroup(op, "Serve options")
    og.add_option("" , "--port", default=8080,
                  metavar="PORT", type="int",
                  help="port for serving (default: 8080)")
    op.add_option_group(og)

    opts, args = op.parse_args()

    if opts.build + opts.serve < 1:
        op.print_help()
        op.exit()

    opts.project = args and args[0] or "."

    return opts

# =============================================================================
# main
# =============================================================================

def main():

    opts = options()

    if opts.build:
        build(opts.project, opts)
    if opts.serve:
        serve(opts.project, opts.port)

if __name__ == '__main__':

    main()
