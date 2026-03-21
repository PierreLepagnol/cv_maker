# XeLaTeX configuration for latexmk
$pdf_mode = 5;           # Use xelatex
$xelatex = 'xelatex -interaction=nonstopmode -halt-on-error %O %S';
$out_dir = '.';
$clean_ext = 'synctex.gz synctex.gz(busy) run.xml tex.bak bbl bcf fls nav snm vrb';
$silent = 0;
