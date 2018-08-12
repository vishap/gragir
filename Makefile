
TEST_FILES = $(wildcard samples/*.zip)

.PHONY: test
test:
	python gragir/__main__.py -v samples/algorithms_third_edition_in_c.zip algorithms_third_edition_in_c.epub

.PHONY: test_all
test_all: $(addprefix test_,$(TEST_FILES))


.PHONY: $(addprefix test_,$(TEST_FILES))
$(addprefix test_,$(TEST_FILES)): test_%:
	@echo Testing $*
	@python gragir/__main__.py -v $* test_out/$(*F).epub

#python gragir/__main__.py samples/algorithms_third_edition_in_c.zip algorithms_third_edition_in_c.epub

.PHONY: setup
setup:
	git submodule update


