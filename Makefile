
TEST_FILES = $(wildcard samples/*.zip)

PYTHONPATH = $(CURDIR)/modules/ebooklib

.PHONY: test
test: test_samples/algorithms_third_edition_in_c.zip 

.PHONY: test_all
test_all: $(addprefix test_,$(TEST_FILES))


.ONESHELL:
.PHONY: $(addprefix test_,$(TEST_FILES))
$(addprefix test_,$(TEST_FILES)): test_%:
	@echo Testing $*
	@set PYTHONPATH=$(PYTHONPATH) && python gragir/__main__.py -v $* test_out/$(*F).epub

#python gragir/__main__.py samples/algorithms_third_edition_in_c.zip algorithms_third_edition_in_c.epub

.PHONY: setup
setup:
	git submodule update


