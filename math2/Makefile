LATEXMK := latexmk
TARGET := main.pdf
SOURCE := main.tex
TEXFILES := $(wildcard *.tex)

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(TEXFILES)
	$(LATEXMK) -pdfdvi -latex='uplatex %O %S' -interaction=nonstopmode -halt-on-error $(SOURCE)

clean:
	$(LATEXMK) -C $(SOURCE)
