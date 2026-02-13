import sys

def pytest_collect_file(parent, file_path):
    if file_path.suffix == ".py" and file_path.name.startswith("test_"):
        solution_dir = file_path.parent.parent / "solution"
        if solution_dir.exists() and str(solution_dir) not in sys.path:
            sys.path.insert(0, str(solution_dir))