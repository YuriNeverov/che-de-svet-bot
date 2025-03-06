import sys
import os
import unittest

project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

if __name__ == '__main__':
  loader = unittest.TestLoader()
  suite = loader.discover(start_dir=os.path.join(project_root, 'test'),
                          pattern='*Test.py',
                          top_level_dir=project_root)

  print("\nRunning tests...")
  runner = unittest.TextTestRunner(verbosity=2)
  result = runner.run(suite)

  print("\nTest results:")
  print(f"Tests run: {result.testsRun}")
  print(f"Failures: {len(result.failures)}")
  print(f"Errors: {len(result.errors)}")
