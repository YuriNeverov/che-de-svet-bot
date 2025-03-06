import sys
import unittest

from pathlib import Path

project_root = Path(__file__).parent.absolute()
sys.path.insert(0, project_root.as_posix())

if __name__ == '__main__':
  loader = unittest.TestLoader()
  suite = loader.discover(start_dir=(project_root / 'test').as_posix(),
                          pattern='*Test.py',
                          top_level_dir=project_root.as_posix())

  print("\nRunning tests...")
  runner = unittest.TextTestRunner(verbosity=2)
  result = runner.run(suite)

  print("\nTest results:")
  print(f"Tests run: {result.testsRun}")
  print(f"Failures: {len(result.failures)}")
  print(f"Errors: {len(result.errors)}")
