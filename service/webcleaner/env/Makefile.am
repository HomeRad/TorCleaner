EXTRA_DIST = LANG LC_ALL LC_CTYPE WC_DEVELOPMENT

data_DATA = PYTHONPATH PATH LANG LC_ALL LC_CTYPE WC_DEVELOPMENT

# both PATH and PYTHONPATH should contain the top builddir for local
# testing
PYTHONPATH PATH:
if BUILD_WINDOWS
else
	echo `readlink -f "$(top_builddir)"` > $@
endif


clean-local:
	rm -f PYTHONPATH PATH
