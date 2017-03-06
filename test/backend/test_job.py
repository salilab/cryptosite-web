import unittest
import cryptosite
import saliweb.test
import saliweb.backend
import os

class JobTests(saliweb.test.TestCase):
    """Check custom CryptoSite Job class"""

    def test_stage(self):
        """Test Stage class"""
        t = saliweb.test.RunInTempDir()
        self.assertEqual(cryptosite.Stage.read(), None)
        cryptosite.Stage.write('foo')
        self.assertEqual(cryptosite.Stage.read(), 'foo')
        os.unlink('stage.out')
        self.assertEqual(cryptosite.Stage.read(), None)
        cryptosite.Stage.write('foo')
        cryptosite.Stage.write(None)
        self.assertEqual(cryptosite.Stage.read(), None)
        self.assertFalse(os.path.exists('stage.out'))
        cryptosite.Stage.write(None)
        self.assertFalse(os.path.exists('stage.out'))

    def test_random(self):
        """Test determination of random file names"""
        j = self.make_test_job(cryptosite.Job, 'RUNNING')
        d = saliweb.test.RunInDir(j.directory)
        rfil = j._set_random()
        self.assertTrue(os.path.exists('random.out'))
        self.assertEqual(j._get_random(), rfil)

    def test_preprocess(self):
        """Test preprocess"""
        j = self.make_test_job(cryptosite.Job, 'RUNNING')
        for fname in ('stage.out', 'other.out'):
            with open(os.path.join(j.directory, fname), 'w') as fh:
                fh.write("dummy")
        j._run_in_job_directory(j.preprocess)
        self.assertEqual(os.listdir(j.directory), ['other.out'])

    def test_run_first_stepok(self):
        """Test successful run method, first step"""
        j = self.make_test_job(cryptosite.Job, 'RUNNING')
        fname = os.path.join(j.directory, 'param.txt')
        open(fname, 'w').write('testpdb\nA\n')
        cls = j._run_in_job_directory(j.run)
        self.assert_(isinstance(cls, saliweb.backend.SGERunner),
                     "SGERunner not returned")

if __name__ == '__main__':
    unittest.main()
