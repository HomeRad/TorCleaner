EXTRA_DIST = PATH LANG LC_ALL LC_CTYPE WC_DEVELOPMENT

data_SOURCES: PYTHONPATH PATH

# both PATH and PYTHONPATH should contain the top builddir for local
# testing
PYTHONPATH PATH:
	echo "$(top_builddir)" > $<


