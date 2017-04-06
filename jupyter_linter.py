
import os
import argparse
import collections
import json
import re
import sys
import fnmatch

NotebookError = collections.namedtuple('NotebookError', ['filename', 'msg'])


def main():
    parser = argparse.ArgumentParser(description='A linter for Jupyter Notebooks')
    parser.add_argument('folder', help='The folder containing Jupyter Notebooks')
    args = parser.parse_args()

    notebook_filenames = _get_notebook_filenames_in_folder(args.folder)
    print('Found %d notebooks' % len(notebook_filenames))

    all_errors = []
    for notebook_filename in notebook_filenames:
        with open(notebook_filename) as notebook_file:
            notebook = json.load(notebook_file)
            errors = _run_notebook_checks(notebook_filename, notebook)
            all_errors.append(errors)
    if all_errors:
        _print_error_report(all_errors)
        sys.exit(2)
    print('All good!')


def _get_notebook_filenames_in_folder(folder):
    if not os.path.exists(folder):
        print('%s does not exist!' % folder)
        sys.exit(1)

    notebook_files = []
    for root, unused_dirnames, filenames in os.walk(folder):
        if '/.ipynb_checkpoints' in root:
            continue
        for filename in fnmatch.filter(filenames, '*.ipynb'):
            notebook_files.append(os.path.join(root, filename))
    return notebook_files


def _run_notebook_checks(file_name, notebook):
    errors = []
    check_functions = [
        _check_import_in_first_code_cell,
        _check_at_least_one_cell,
        _check_first_cell_contains_author,
        _check_python3,
        _check_no_spaces_in_filenames,
        _check_clean_execution,
    ]
    for check_function in check_functions:
        errors.extend(check_function(file_name, notebook))
    return errors


def _print_error_report(all_errors):
    # TODO: Improve error reporting (add colors, consistent schema for all errors).
    for error in all_errors:
        print(error)


def _check_import_in_first_code_cell(file_name, notebook):
    errors = []
    coding_cells = [
        c for c in notebook.get('cells', [])
        if c.get('cell_type') == 'code']
    for i, coding_cell in enumerate(coding_cells[1:]):
        for line in coding_cell.get('source', []):
            if re.match('^import ', line) or re.match('^from .* import ', line):
                msg = (
                    'Imports should be only in first coding cell, but in '
                    'file "%s", coding cell %d' % (file_name, i + 1))
                errors.append(NotebookError(file_name, msg))
    return errors


def _check_at_least_one_cell(file_name, notebook):
    """Check that each notebook contains at least one cell."""
    if len(notebook.get('cells', [])) == 0:
        msg = '%s has no cells' % file_name
        return [NotebookError(file_name, msg)]
    return []


def _check_first_cell_contains_author(file_name, notebook):
    """Check that the first cell is a markdown cell with the author."""
    errors = []
    cells = notebook.get('cells', [])
    if not cells:
        return errors
    first_cell = cells[0]
    msg = (
        'First cell of %s should be a markdown cell containing the '
        "original author's name" % file_name)
    if first_cell.get('cell_type') != 'markdown':
        errors.append(NotebookError(file_name, msg))
        return errors
    author_found = False
    for line in first_cell.get('source', []):
        if line.startswith('Author: ') or line.startswith('Authors: '):
            author_found = True
            break
    if not author_found:
        errors.append(NotebookError(file_name, msg))
    return errors


def _check_python3(file_name, notebook):
    """Check that the notebooks are using Python 3 kernel only."""
    kernel = notebook['metadata']['kernelspec'].get('name')
    if kernel != 'python3':
        msg = (
            'The notebook %s is using kernel %s instead of python3'
            % (file_name, kernel))
        return [NotebookError(file_name, msg)]
    return []


def _check_no_spaces_in_filenames(file_name, unused_notebook):
    """Check that the notebooks names use underscores, not blank spaces."""
    if ' ' in os.path.basename(file_name):
        msg = 'Use underscore in filename %s' % file_name
        return [NotebookError(file_name, msg)]
    return []


def _check_clean_execution(file_name, notebook):
    """Check that all code cells have been executed once in the right order."""
    errors = []
    cells = notebook.get('cells', [])
    code_cells = [c for c in cells if c.get('cell_type') == 'code']
    for index, cell in enumerate(code_cells):
        if not cell.get('source'):
            msg = 'There is an empty code cell in notebook %s' % file_name
            errors.append(NotebookError(file_name, msg))
        if cell.get('execution_count') != index + 1:
            msg = (
                'The code cells in notebook %s have not been executed '
                'in the right order. Run "Kernel > Restart & run all" '
                'then save the notebook.' % file_name)
            errors.append(NotebookError(file_name, msg))
            break
    return errors


if __name__ == '__main__':
    main()