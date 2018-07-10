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

    anilatex.py "Ani\LaTeX" -D 600 -o anilatex.png

LaTeX support: ![One proof that pi is bounded upwards by 22/7](https://github.com/FYPetro/AniLaTeX/blob/master/image/pi-bound.png)

    anilatex.py "$\displaystyle 0<\int_{0}^{1}\frac{x^{4}(1-x)^{4}}{1+x^{2}}\ dx=\frac{22}{7}-\pi$" -o pi-bound.png

CJK support: ![CJK support](https://github.com/FYPetro/AniLaTeX/blob/master/image/cjk.png)

    anilatex.py "{\Chi 中文与}{\Jpn 日本語と}{\Kor 한국어}" -o cjk.png -t standalone-cjk

