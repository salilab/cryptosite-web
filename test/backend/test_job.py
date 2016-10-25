import unittest
import cryptosite
import saliweb.test
import saliweb.backend
import os

class JobTests(saliweb.test.TestCase):
    """Check custom CryptoSite Job class"""

    def test_run_first_stepok(self):
        """Test successful run method, first step"""
        j = self.make_test_job(cryptosite.Job, 'RUNNING')
        fname = os.path.join(j.directory, 'param.txt')
        open(fname, 'w').write('testjob\ntest@example.com\nA\n')
        cls = j._run_in_job_directory(j.run)
        self.assert_(isinstance(cls, saliweb.backend.SGERunner),
                     "SGERunner not returned")

if __name__ == '__main__':
    unittest.main()
