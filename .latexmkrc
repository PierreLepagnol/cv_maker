# LaTeX build configuration for latexmk
$pdf_mode = 1;           # Generate PDF using pdflatex
$pdflatex = 'pdflatex -interaction=nonstopmode -halt-on-error';
$out_dir = '.';          # Output in current directory
$clean_ext = 'synctex.gz synctex.gz(busy) run.xml tex.bak bbl bcf fls nav snm vrb';

# Silence warnings
$silent = 0;
