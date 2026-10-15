LATEXMK := latexmk
TARGET := manu
.PHONY: all pdf clean distclean
all: pdf
pdf: $(TARGET).pdf
$(TARGET).pdf: $(TARGET).tex
	$(LATEXMK) -pdfdvi -latex='platex %O %S' \
		-e '$$dvipdf = q/dvipdfmx %O -o %D %S/;' \
		-interaction=nonstopmode -halt-on-error $(TARGET).tex
clean:
	$(LATEXMK) -c $(TARGET).tex
distclean:
	$(LATEXMK) -C $(TARGET).tex
