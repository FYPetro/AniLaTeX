![AniLaTeX logo](https://github.com/FYPetro/AniLaTeX/blob/master/image/anilatex.png)

# AniLaTeX
Test project.

# Prerequisites
1. Windows or Ubuntu
2. Python 3
3. XeLaTeX
4. GhostScript

Install the prerequisites then add relevant directories to the system-wide `Path` (Windows) or `$PATH` (*nix)

# Examples
Generate the logo:

    anilatex.py "Ani\LaTeX" -D 600 -o anilatex

LaTeX support: ![One proof that pi is bounded upwards by 22/7](https://github.com/FYPetro/AniLaTeX/blob/master/image/pi-bound.png)

    anilatex.py "$\displaystyle 0<\int_{0}^{1}\frac{x^{4}(1-x)^{4}}{1+x^{2}}\ dx=\frac{22}{7}-\pi$" -o pi-bound

CJK support: ![CJK support](https://github.com/FYPetro/AniLaTeX/blob/master/image/cjk.png)

    anilatex.py "{\Chi 中文与}{\Jpn 日本語と}{\Kor 한국어}" -cjk -o cjk

`bclogo` package wrapper:

![bclogo example](https://github.com/FYPetro/AniLaTeX/blob/master/image/bclogo.png)

    anilatex.py "LaTeX is a document preparation system. When writing, the writer uses plain text as opposed to the formatted text found in WYSIWYG (``what you see is what you get'') word processors like Microsoft Word, LibreOffice Writer and Apple Pages. The writer uses markup tagging conventions to define the general structure of a document (such as article, book, and letter) to stylise text throughout a document (such as bold and italics), and to add citations and cross-references. A TeX distribution such as TeX Live or MikTeX is used to produce an output file (such as PDF or DVi) suitable for printing or digital distribution. Within the typesetting system, its name is stylised as \LaTeX. {\Kor 위 단락} {\Chi 节选自} {\Jpn ウイキペディア} on \today." --title "What is \LaTeX?" --option "logo={\bcattention}" -cjk -t bclogo -D 72 -o bclogo
