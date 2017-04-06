"""Unit tests for the jupyter_linter module."""
import jupyter_linter


def _create_cell(**kwargs):
    cell = {
        'cell_type': 'code',
        'execution_count': 1,
        'metadata': {},
        'outputs': [],
        'source': []
    }
    cell.update(kwargs)
    return cell


class TestFirstCellImport(object):
    """All imports should happen in the first cell of a notebook."""

    def test_import_only_in_first_cell(self):
        notebook = {
            'cells': [_create_cell(source=['import bla from blub'])],
        }
        errors = jupyter_linter._check_import_in_first_code_cell(notebook)
        assert(not errors)

    def test_import_only_in_first_cell_two_cells(self):
        notebook = {
            'cells': [
                _create_cell(source=['import bla from blub']),
                _create_cell(source=['print("stuff")']),
            ],
        }
        errors = jupyter_linter._check_import_in_first_code_cell(notebook)
        assert(not errors)

    def test_import_in_other_than_first_cell(self):
        notebook = {
            'cells': [
                _create_cell(source=['print("stuff")']),
                _create_cell(source=['import bla from blub']),
            ],
        }
        errors = jupyter_linter._check_import_in_first_code_cell(notebook)
        assert(len(errors) == 1)
        assert(errors[0].msg == (
            'Imports found in coding cell 1. Please move imports to first coding cell'))


class TestNotebookNotEmpty(object):
    """A notebook should contain at least one cell."""

    def test_empty_notebook(self):
        notebook = {
            'cells': [],
        }
        errors = jupyter_linter._check_at_least_one_cell(notebook)
        assert(len(errors) == 1)

    def test_with_one_cell(self):
        notebook = {
            'cells': [_create_cell()],
        }
        errors = jupyter_linter._check_at_least_one_cell(notebook)
        assert(not errors)


class TestAuthorInFirstCell(object):
    """Each notebook should start with a markdown cell containing the author of the notebook."""

    def test_does_not_fail_with_empty_notebook(self):
        """Empty notebooks are captured by another test."""
        notebook = {
            'cells': [],
        }
        errors = jupyter_linter._check_first_cell_contains_author(notebook)
        assert(not errors)

    def test_first_cell_not_markdown(self):
        notebook = {
            'cells': [_create_cell(cell_type='code')],
        }
        errors = jupyter_linter._check_first_cell_contains_author(notebook)
        assert(len(errors) == 1)

    def test_first_cell_no_author(self):
        notebook = {
            'cells': [_create_cell(cell_type='markdown', source=['Bla bla bla'])],
        }
        errors = jupyter_linter._check_first_cell_contains_author(notebook)
        assert(len(errors) == 1)

    def test_first_cell_contains_author(self):
        notebook = {
            'cells': [_create_cell(cell_type='markdown', source=['Author: Stephan'])],
        }
        errors = jupyter_linter._check_first_cell_contains_author(notebook)
        assert(not errors)


class TestKernelVersion(object):
    """All notebooks should be written using Python 3"""

    def test_wrong_kernel(self):
        notebook = {
            'metadata': {
                'kernelspec': {
                    'display_name': 'Python 3',
                    'language': 'python',
                    'name': 'ruby'
                },
            },
        }
        errors = jupyter_linter._check_python3(notebook)
        assert(len(errors) == 1)

    def test_python3_kernel(self):
        notebook = {
            'metadata': {
                'kernelspec': {
                    'display_name': 'Python 3',
                    'language': 'python',
                    'name': 'python3'
                },
            },
        }
        errors = jupyter_linter._check_python3(notebook)
        assert(not errors)


class TestFilename(object):
    """Notebooks should use underscores in filenames instead of spaces."""

    def test_whitespace_in_filename(self):
        errors = jupyter_linter._check_no_spaces_in_filenames({}, 'file name.ipynb')
        assert(len(errors) == 1)

    def test_snake_case_filename(self):
        errors = jupyter_linter._check_no_spaces_in_filenames({}, 'file_name.ipynb')
        assert(not errors)


class TestCleanExecution(object):
    """Make sure that all code cells in the notebook were executed in order."""

    def test_no_empty_code_cells(self):
        notebook = {
            'cells': [_create_cell(cell_type='code', source=[])]
        }
        errors = jupyter_linter._check_clean_execution(notebook)
        assert(len(errors) == 1)

    def test_cells_not_executed_in_order(self):
        notebook = {
            'cells': [_create_cell(cell_type='code', execution_count=2, source=['stuff'])]
        }
        errors = jupyter_linter._check_clean_execution(notebook)
        assert(len(errors) == 1)

    def test_cells_executed_in_order(self):
        notebook = {
            'cells': [
                _create_cell(cell_type='code', execution_count=1, source=['stuff']),
                _create_cell(cell_type='code', execution_count=2, source=['other stuff']),
            ]
        }
        errors = jupyter_linter._check_clean_execution(notebook)
        assert(not errors)
