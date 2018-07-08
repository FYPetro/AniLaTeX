#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import errno
import os
import re
import subprocess
from shutil import copy2

# Global variables.
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DPI = 72


# Global regular expressions.
REGEX = {
    'print': r'显示“(.*)”。'
}


def print_latex(body, workspace, template=None, preamble=None, filename='temp', dpi=None):
    """Produce and compile a standalone LaTeX file"""
    document = """
        \\documentclass[preview]{standalone}
        \\input{anilatex-preamble}
        \\begin{document}
        \\input{anilatex-body}
        \\end{document}
    """
    if template is not None:
        template_path = os.path.join(PROJECT_DIR, 'template', '{}.tex'.format(template))
        with open(template_path, 'r', encoding='utf-8') as file:
            document = file.read()
    document = document.replace('\\input{anilatex-preamble}', preamble or '')
    document = document.replace('\\input{anilatex-body}', body)
    tex_path = os.path.join(workspace, '{}.tex'.format(filename))
    pdf_path = os.path.join(workspace, '{}.pdf'.format(filename))
    png_path = os.path.join(workspace, '{}.png'.format(filename))
    with open(tex_path, 'w', encoding='utf-8') as file:
        file.write(document)
    #with open(os.devnull, 'w') as devnull:
    subprocess.run(['xelatex', tex_path],
        cwd=workspace)#, stdout=devnull)
    dpi = dpi or DEFAULT_DPI
    subprocess.run(['gswin64c', '-dSAFER', '-dBATCH', '-dNOPAUSE',
        '-r{}'.format(dpi*3), '-DownScaleFactor={}'.format(3), '-dGraphicsAlphaBits=4', '-sDEVICE=pngalpha',
        '-sOutputFile={}'.format(png_path), pdf_path],
        cwd=workspace)#, stdout=devnull)
    # subprocess.run(['dvipng', dvi_path,
    #     '-o', png_path, '-D', '{}'.format(dpi or DEFAULT_DPI)],
    #     cwd=workspace)#, stdout=devnull)


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
    parser.add_argument('--demo', nargs='?', const='hello_world',
        help='name of demo to be executed', metavar='demo_name')
    args = parser.parse_args()

    if args.output is None:
        args.output = 'text'
    
    if args.text is not None:
        directory = os.path.join(PROJECT_DIR, 'demo', 'ws')
        png_path = os.path.join(directory, '{}.png'.format(args.output))
        try:
            os.makedirs(directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        print_latex(args.text, directory,
            filename=args.output, dpi=args.outres, template=args.template)
        copy2(png_path, os.getcwd())
    elif args.demo is not None:
        path = os.path.join(PROJECT_DIR, 'demo', args.demo)
        parse_animath(path)
    elif args.input is not None:
        parse_animath(args.input)
    else:
        parser.print_help()
