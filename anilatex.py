#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import configparser
import errno
import logging
import os
import re
import subprocess
from shutil import copy2

# Global variables.
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


# Global regular expressions.
REGEX = {
    'print': r'显示“(.*)”。',
    'parameter': r'^--([a-zA-Z][a-zA-Z0-9]*)$'
}


def print_latex(body, workspace, filename='temp', template=None, cjk=False, dpi=None, placeholder={}):
    """Produce and compile a standalone LaTeX file"""
    document = """\\documentclass[preview,margin=1pt]{standalone}
\\usepackage{amsmath}
\\input{AniLaTeX-preamble}
\\begin{document}
\\input{AniLaTeX-body}
\\end{document}
"""
    cjk_preamble = """\\usepackage{{fontspec}}
\\usepackage{{xeCJK}}
% Reference: https://tex.stackexchange.com/a/45403
\\setCJKfamilyfont{{zhrm}}{{{}}}
\\setCJKfamilyfont{{jarm}}{{{}}}
\\setCJKfamilyfont{{korm}}{{{}}}
\\newcommand\\Chi{{\\CJKfamily{{zhrm}}\\CJKnospace}}
\\newcommand\\Jpn{{\\CJKfamily{{jarm}}\\CJKnospace}}
\\newcommand\\Kor{{\\CJKfamily{{korm}}\\CJKnospace}}
""".format(DEFAULT_FONT['chinese'], DEFAULT_FONT['japanese'], DEFAULT_FONT['korean'])
    default_inputs = {
        'preamble': '',
    }
    for key, value in default_inputs.items():
        if key not in placeholder:
            placeholder[key] = value

    if cjk is True:
        placeholder['preamble'] = cjk_preamble + placeholder['preamble']

    if template is not None:
        template_path = os.path.join(PROJECT_DIR, 'template', '{}.tex'.format(template))
        with open(template_path, 'r', encoding='utf-8') as file:
            document = file.read()

    document = document.replace('\\input{AniLaTeX-CJKChinese}', DEFAULT_FONT['chinese'])
    document = document.replace('\\input{AniLaTeX-CJKJapanese}', DEFAULT_FONT['japanese'])
    document = document.replace('\\input{AniLaTeX-CJKKorean}', DEFAULT_FONT['korean'])
    document = document.replace('\\input{AniLaTeX-body}', body)
    for key, value in placeholder.items():
        document = document.replace('\\input{AniLaTeX-' + key + '}', value)

    tex_path = os.path.join(workspace, '{}.tex'.format(filename))
    pdf_path = os.path.join(workspace, '{}.pdf'.format(filename))
    png_path = os.path.join(workspace, '{}.png'.format(filename))
    with open(tex_path, 'w', encoding='utf-8') as file:
        file.write(document)
    tex_backend = 'xelatex'
    subprocess.run([tex_backend, tex_path], cwd=workspace)
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
    parser.add_argument('text', nargs='?',
        help='text to write (bypass -i and --demo if provided)')
    parser.add_argument('-D', nargs='?', type=int, const=DEFAULT_DPI,
        help='output resolution of text', metavar='dpi', dest='outres')
    parser.add_argument('-i', nargs='?',
        help='name of script to be parsed', metavar='input_file', dest='input')
    parser.add_argument('-o', nargs='?',
        help='name of output file', metavar='output_file', dest='output')
    parser.add_argument('-t', nargs='?',
        help='name of template file', metavar='template_file', dest='template')
    parser.add_argument('-cjk', action='store_true',
        help='enable xeCJK package', dest='cjk')
    parser.add_argument('--demo', nargs='?', const='hello_world',
        help='name of demo to be executed', metavar='demo_name')
    args, unknown = parser.parse_known_args()

    if args.output is None:
        args.output = 'text'

    # Parse --key value pairs
    parameter = {}
    truly_unknown = []
    for index in range(0,len(unknown)):
        scurrent = re.search(REGEX['parameter'], unknown[index])
        if scurrent and index + 1 < len(unknown) and not re.search(REGEX['parameter'], unknown[index + 1]):
            key = scurrent.group(1)
            value = unknown[index + 1]
            parameter[scurrent.group(1)] = unknown[index + 1]
        else:
            truly_unknown.append(unknown[index])

    if args.text is not None:
        """Turn text into still image"""
        directory = os.path.join(PROJECT_DIR, 'demo', 'ws')
        png_path = os.path.join(directory, '{}.png'.format(args.output))
        try:
            os.makedirs(directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        print_latex(args.text, directory,
            filename=args.output, dpi=args.outres, template=args.template,
            cjk=args.cjk, placeholder=parameter)
        copy2(png_path, os.getcwd())
    elif args.demo is not None:
        """Turn AniLaTeX demo file into still image"""
        path = os.path.join(PROJECT_DIR, 'demo', args.demo)
        parse_animath(path)
    elif args.input is not None:
        """Turn AniLaTeX file into still image"""
        parse_animath(args.input)
    else:
        """On the top of the hill is a lonely help page"""
        parser.print_help()
