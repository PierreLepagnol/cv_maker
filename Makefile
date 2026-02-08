.PHONY: academic industry all clean help

academic:
	uv run build.py academic

industry:
	uv run build.py industry

all:
	uv run build.py all

clean:
	rm -rf build/
	find . -name "*.aux" -o -name "*.log" -o -name "*.fdb_latexmk" -o -name "*.fls" -o -name "*.out" -o -name "*.synctex.gz" | xargs rm -f

help:
	@echo "Available targets:"
	@echo "  make academic  - Build academic CV variant"
	@echo "  make industry  - Build industry CV variant"
	@echo "  make all       - Build all CV variants"
	@echo "  make clean     - Remove generated files"
	@echo "  make help      - Show this help message"
