"""Standalone runner for etl_validator - fixes import issues"""
import sys
import os

# Add src to Python path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

print(f"Python path: {sys.path[0]}")
print(f"Src path: {src_path}")
print(f"Working directory: {os.getcwd()}")

# Import and run
try:
    # Absolute import from cli module
    import cli.main
    print("Successfully imported cli.main module")

    if __name__ == '__main__':
        print("Starting ETL Validator...")
        sys.exit(cli.main.main())
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    print(f"Attempting alternative import...")

    # Try alternative: import as package
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "cli.main",
            os.path.join(src_path, "cli", "main.py")
        )
        cli_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cli_module)
        print("Successfully loaded cli.main via importlib")
        sys.exit(cli_module.main())
    except Exception as e2:
        print(f"Alternative import also failed: {e2}")
        sys.exit(1)

