![AniLaTeX logo](https://github.com/FYPetro/AniLaTeX/blob/master/image/anilatex.png)

# AniLaTeX
Test project.

# Prerequisites
1. Windows
2. Python 3
3. XeLaTeX
4. GhostScript

# Usage

Generate the logo:

    anilatex.py "Ani\LaTeX" -D 600 -o anilatex.png

LaTeX support: ![One proof that pi is bounded upwards by 22/7](https://github.com/FYPetro/AniLaTeX/blob/master/image/pi-bound.png)
    
    anilatex.py "$\displaystyle 0<\int_{0}^{1}\frac{x^{4}(1-x)^{4}}{1+x^{2}}\ dx=\frac{22}{7}-\pi$" -o pi-bound.png

CJK support: ![CJK support](https://github.com/FYPetro/AniLaTeX/blob/master/image/cjk.png)
    
    anilatex.py "中文と日本語" -o cjk.png -t standalone-cjk
    
