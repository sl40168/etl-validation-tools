"""Standalone runner for etl_validator - sets up proper package structure"""
import sys
import os

# Get project root directory
project_root = os.path.dirname(os.path.abspath(__file__))

# Add project root to Python path so imports work
sys.path.insert(0, project_root)

print(f"Project root: {project_root}")
print(f"Working directory: {os.getcwd()}")
print(f"Python path[0]: {sys.path[0]}")

# Import as module from project root
try:
    from src.cli.main import main
    print("✓ Successfully imported src.cli.main")

    if __name__ == '__main__':
        print("✓ Starting ETL Validator...")
        exit_code = main()
        print(f"✓ Exit code: {exit_code}")
        sys.exit(exit_code)
except ImportError as e:
    print(f"✗ Import error: {e}")
    print(f"\nPython path:")
    for i, p in enumerate(sys.path[:5]):
        print(f"  [{i}] {p}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Runtime error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
