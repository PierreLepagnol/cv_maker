MAKEFLAGS += -j

DATA ?= data/resume.yaml

.PHONY: academic industry industry-footer sciam \
        academic-single academic-twocol academic-twocol-footer \
        minimal-single minimal-twocol minimal-twocol-footer \
        bold-single bold-twocol bold-twocol-footer \
        all clean help

# Named variants
academic:
	uv run build.py academic --output-dir out/academic --data $(DATA)

industry:
	uv run build.py industry --output-dir out/industry --data $(DATA)

industry-footer:
	uv run build.py industry-footer --output-dir out/industry-footer --data $(DATA)

sciam:
	uv run build.py sciam --output-dir out/sciam --data $(DATA)

# All theme × layout combinations
academic-single:
	uv run build.py --theme academic --layout single --output-dir out/academic-single --data $(DATA)

academic-twocol:
	uv run build.py --theme academic --layout twocol --output-dir out/academic-twocol --data $(DATA)

academic-twocol-footer:
	uv run build.py --theme academic --layout twocol-footer --output-dir out/academic-twocol-footer --data $(DATA)

minimal-single:
	uv run build.py --theme minimal --layout single --output-dir out/minimal-single --data $(DATA)

minimal-twocol:
	uv run build.py --theme minimal --layout twocol --output-dir out/minimal-twocol --data $(DATA)

minimal-twocol-footer:
	uv run build.py --theme minimal --layout twocol-footer --output-dir out/minimal-twocol-footer --data $(DATA)

bold-single:
	uv run build.py --theme bold --layout single --output-dir out/bold-single --data $(DATA)

bold-twocol:
	uv run build.py --theme bold --layout twocol --output-dir out/bold-twocol --data $(DATA)

bold-twocol-footer:
	uv run build.py --theme bold --layout twocol-footer --output-dir out/bold-twocol-footer --data $(DATA)

all: academic-single academic-twocol academic-twocol-footer \
     minimal-single minimal-twocol minimal-twocol-footer \
     bold-single bold-twocol bold-twocol-footer

clean:
	rm -rf out build

help:
	@printf '%s\n' \
	  'make academic' \
	  'make industry' \
	  'make industry-footer' \
	  'make sciam' \
	  'make all'
