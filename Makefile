MAKEFLAGS += -j

.PHONY: academic industry industry-footer sciam \
        academic-single academic-twocol academic-twocol-footer \
        minimal-single minimal-twocol minimal-twocol-footer \
        bold-single bold-twocol bold-twocol-footer \
        all clean help

# Named variants
academic:
	uv run build.py academic --output-dir out/academic

industry:
	uv run build.py industry --output-dir out/industry

industry-footer:
	uv run build.py industry-footer --output-dir out/industry-footer

sciam:
	uv run build.py sciam --output-dir out/sciam

# All theme × layout combinations
academic-single:
	uv run build.py --theme academic --layout single --output-dir out/academic-single

academic-twocol:
	uv run build.py --theme academic --layout twocol --output-dir out/academic-twocol

academic-twocol-footer:
	uv run build.py --theme academic --layout twocol-footer --output-dir out/academic-twocol-footer

minimal-single:
	uv run build.py --theme minimal --layout single --output-dir out/minimal-single

minimal-twocol:
	uv run build.py --theme minimal --layout twocol --output-dir out/minimal-twocol

minimal-twocol-footer:
	uv run build.py --theme minimal --layout twocol-footer --output-dir out/minimal-twocol-footer

bold-single:
	uv run build.py --theme bold --layout single --output-dir out/bold-single

bold-twocol:
	uv run build.py --theme bold --layout twocol --output-dir out/bold-twocol

bold-twocol-footer:
	uv run build.py --theme bold --layout twocol-footer --output-dir out/bold-twocol-footer

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
