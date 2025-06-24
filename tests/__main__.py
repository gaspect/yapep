import unittest

if __name__ == '__main__':
    # Discover and run all tests in the tests directory
    test_suite = unittest.defaultTestLoader.discover('')
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Print a summary of the test results
    print("\nTest Summary:")
    print(f"Ran {result.testsRun} tests")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    # Exit with non-zero status if there were failures or errors
    import sys
    if result.failures or result.errors:
        sys.exit(1)