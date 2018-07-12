#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import configparser
import datetime
import errno
import logging
import os
import re
import subprocess
from _version import __version__
from shutil import copy2, rmtree

# Global variables
config = configparser.ConfigParser()
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DPI = 42
if os.name == 'nt':
    DEFAULT_FONT = {
        'chinese': 'SimSun',
        'japanese': 'MS Mincho',
        'korean': 'Malgun Gothic'
    }
else:
    DEFAULT_FONT = {
        'chinese': 'AR PL SungtiL GB',
        'japanese': 'TakaoMincho',
        'korean': 'Baekmuk Batang'
    }


# Global regular expressions
REGEX = {
    'print': r'显示“(.*)”。',
    'parameter': r'^--([a-zA-Z][a-zA-Z0-9]*)$',
    'placeholder': r'\\input{AniLaTeX-([a-zA-Z][a-zA-Z0-9]+)(?::([0-9]+))?(?:={(.*?)})?}',
    'section': r'(\\begin{AniLaTeX-(([a-zA-Z][a-zA-Z0-9]+?)(?::([0-9]+))?)}).*?(\\end{AniLaTeX-\2})'
}

def format_usepackage(package, options=[]):
    """Formats package options as usepackage directives"""
    if len(options) == 0:
        return '\\usepackage{{{}}}'.format(package)
    else:
        return '\\usepackage[{}]{{{}}}'.format(','.join(options), package)


def print_latex(body, workspace, filename='temp', template=None, dpi=None, placeholder={}, package=[]):
    """Produce and compile a standalone LaTeX file"""
    document = """\\documentclass[preview,margin=\\input{AniLaTeX-margin={0pt}}]{\\input{AniLaTeX-documentclass={standalone}}}
\\input{AniLaTeX-preamble}
\\begin{document}
\\input{AniLaTeX-body}
\\end{document}
"""
    # Set default argument for placeholders
    default_inputs = {
        'preamble': '',
        'fontchi': DEFAULT_FONT['chinese'],
        'fontjpn': DEFAULT_FONT['japanese'],
        'fontkor': DEFAULT_FONT['korean'],
        'version': __version__,
        'date': datetime.datetime.today().strftime('%Y-%m-%d')
    }
    for key, value in default_inputs.items():
        if key not in placeholder:
            placeholder[key] = value

    # Prepare usepackage directives
    if len(package) > 0:
        usepackage_preamble = os.linesep.join([format_usepackage(x[0],x[1:]) for x in package])
        placeholder['preamble'] = os.linesep.join([usepackage_preamble, placeholder['preamble']])

    # Use provided template
    if template is not None:
        template_path = os.path.join(PROJECT_DIR, 'template', '{}.tex'.format(template))
        with open(template_path, 'r', encoding='utf-8') as file:
            document = file.read()

    # Repeatedly turning off sections
    replaced = None
    while replaced is not False:
        replaced = False
        for s in re.finditer(REGEX['section'], document, flags=re.S):
            replaced = True
            key = s.group(3)
            index = int(s.group(4) or '1')
            # Body section:     \begin{AniLaTeX-body:1}
            #                   \end{AniLaTeX-body:1}
            # Placeholder text: \begin{AniLaTeX-key}
            #                   \end{AniLaTeX-key}
            if (key == 'body' and index > len(body)) or (not key == 'body' and not key in placeholder):
                document = document.replace(s.group(0), '')
            else:
                document = document.replace(s.group(1), '').replace(s.group(5), '')

    # Repeatedly Replace all placeholders with specified value or default ones
    replaced = None
    while replaced is not False:
        replaced = False
        for s in re.finditer(REGEX['placeholder'], document):
            replaced = True
            key = s.group(1)
            index = int(s.group(2) or '1')
            default_value = s.group(3) or ''
            value = None
            # Body text:        \input{AniLaTeX-body:1={Default}}
            if key == 'body' and 0 < index <= len(body):
                value = body[index - 1]
            # Placeholder text: \input{AniLaTeX-key={Default}}
            elif key in placeholder:
                value = placeholder[key]
            document = document.replace(s.group(0), value or default_value)

    # Workflow: .tex --XeTeX-> .pdf
    tex_path = os.path.join(workspace, '{}.tex'.format(filename))
    pdf_path = os.path.join(workspace, '{}.pdf'.format(filename))
    png_path = os.path.join(workspace, '{}.png'.format(filename))
    with open(tex_path, 'w', encoding='utf-8') as file:
        file.write(document)
    tex_backend = 'xelatex'
    subprocess.run([tex_backend, tex_path], cwd=workspace)

    # Workflow: .pdf --GhostScript-> .png
    dpi = dpi or DEFAULT_DPI
    gs_backend = 'gs'
    if os.name == 'nt':
        gs_backend = 'gswin64c'
    subprocess.run([gs_backend, '-dSAFER', '-dBATCH', '-dNOPAUSE',
        '-r{}'.format(dpi*3), '-DownScaleFactor={}'.format(3),
        '-dGraphicsAlphaBits=4', '-sDEVICE=pngalpha',
        '-sOutputFile={}'.format(png_path), pdf_path],
        cwd=workspace)


def parse_animath(path):
    """Parses an AniMath file"""
    file_name = os.path.splitext(os.path.basename(path))[0]
    directory = os.path.join(os.path.dirname(path), '{}-ws'.format(file_name))
    try:
        os.makedirs(directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    with open(path, 'r', encoding='utf-8') as file:
        commands = file.read().splitlines()
        for command in commands:
            match = re.search(REGEX['print'], command)
            if match:
                print_latex(match.group(1), workspace=directory)


if __name__ == '__main__':
    config.read('{}.ini'.format(os.name))
    DEFAULT_FONT['chinese'] = config.get('Fonts', 'CJKChinese', fallback=DEFAULT_FONT['chinese'])
    DEFAULT_FONT['japanese'] = config.get('Fonts', 'CJKJapanese', fallback=DEFAULT_FONT['japanese'])
    DEFAULT_FONT['korean'] = config.get('Fonts', 'CJKKorean', fallback=DEFAULT_FONT['korean'])

    parser = argparse.ArgumentParser(description='A python script to parse AniMath scripts.')
    parser.add_argument('text', nargs='*',
        help='text to write (bypass -i and --demo if provided)')
    parser.add_argument('-u', nargs='+', action='append',
        help='use optional packages', dest='use')
    parser.add_argument('-p', nargs='+',
        help='use optional preambles', dest='preamble')
    parser.add_argument('-c', action='store_true',
        help='clean the workspace', dest='clean')
    parser.add_argument('-D', nargs='?', type=int, const=DEFAULT_DPI,
        help='output resolution of text', metavar='dpi', dest='dpi')
    parser.add_argument('-i', nargs='?',
        help='name of script to be parsed', metavar='file', dest='input')
    parser.add_argument('-o', nargs='?',
        help='name of output file', metavar='file', dest='output')
    parser.add_argument('-t', nargs='?',
        help='name of template file', metavar='template', dest='template')
    parser.add_argument('-d', nargs='?', const='hello_world',
        help='name of demo to be executed', metavar='demo')
    args, unknown = parser.parse_known_args()

    # Set default output name
    if args.output is None:
        args.output = 'text'

    # Parse placeholder --key value pairs
    parameter = {}
    truly_unknown = []
    for index in range(0,len(unknown)):
        scurrent = re.search(REGEX['parameter'], unknown[index])
        if scurrent and index < len(unknown):
            key = scurrent.group(1)
            value = None
            if index + 1 < len(unknown) and not re.search(REGEX['parameter'], unknown[index + 1]):
                value = unknown[index + 1]
            parameter[key] = value
        else:
            truly_unknown.append(unknown[index])

    # Read and concatenate preambles
    preamble = []
    if args.preamble is not None:
        for filename in args.preamble:
            path = os.path.join(PROJECT_DIR, 'preamble', '{}.tex'.format(filename))
            with open(path, 'r', encoding='utf-8') as file:
                preamble.append(file.read())
        parameter['preamble'] = os.linesep.join(preamble)

    if len(args.text) > 0:
        # Turn text into still image
        directory = os.path.join(PROJECT_DIR, 'demo', 'ws')
        png_path = os.path.join(directory, '{}.png'.format(args.output))
        try:
            os.makedirs(directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        print_latex(args.text, directory,
            filename=args.output, dpi=args.dpi, template=args.template,
            placeholder=parameter, package=args.use or [])
        copy2(png_path, os.getcwd())
    elif args.demo is not None:
        # Turn AniLaTeX demo file into still image
        path = os.path.join(PROJECT_DIR, 'demo', args.demo)
        parse_animath(path)
    elif args.input is not None:
        # Turn AniLaTeX file into still image
        parse_animath(args.input)
    elif not args.clean:
        # On the top of the hill is a lonely help page
        parser.print_help()

    if args.clean:
        # Clean up
        rmtree(os.path.join(PROJECT_DIR, 'demo', 'ws'), ignore_errors=True)
