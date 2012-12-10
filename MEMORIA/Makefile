se = -shell-escape

init:
	fig2ps ./dia/*.fig
	xelatex $(se) informe.tex && bibtex informe && xelatex $(se) informe.tex && xelatex $(se) informe.tex

clean:
	rm -rf informe.aux informe.bbl informe.blg informe.lo* informe.out informe.pdf informe.toc
