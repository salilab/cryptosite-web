import unittest
import cryptosite
import saliweb.test
import saliweb.backend
import os


class JobTests(saliweb.test.TestCase):
    """Check custom CryptoSite Job class"""

    def test_stage(self):
        """Test Stage class"""
        with saliweb.test.temporary_working_directory():
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
        with saliweb.test.working_directory(j.directory):
            rfil = j._set_random()
            self.assertTrue(os.path.exists('random.out'))
            self.assertEqual(j._get_random(), rfil)

    def test_preprocess(self):
        """Test preprocess"""
        j = self.make_test_job(cryptosite.Job, 'RUNNING')
        for fname in ('stage.out', 'other.out', 'XXX_mdl.pdb',
                      'sge-script.sh'):
            with open(os.path.join(j.directory, fname), 'w') as fh:
                fh.write("dummy")
        os.mkdir(os.path.join(j.directory, 'XXX'))
        j._run_in_job_directory(j.preprocess)
        self.assertEqual(os.listdir(j.directory), ['other.out'])

    def test_run_first_stepok(self):
        """Test successful run method, first step"""
        j = self.make_test_job(cryptosite.Job, 'RUNNING')
        fname = os.path.join(j.directory, 'param.txt')
        with open(fname, 'w') as fh:
            fh.write('testpdb\nA\n')
        cls = j._run_in_job_directory(j.run)
        self.assertIsInstance(cls, saliweb.backend.SGERunner)

    def test_run_allosmod(self):
        """Test processing of AllosMod output"""
        j = self.make_test_job(cryptosite.Job, 'RUNNING')
        j._run_in_job_directory(j._set_random)
        cls = j._run_in_job_directory(j.run_allosmod)
        self.assertIsInstance(cls, saliweb.backend.SGERunner)

    def test_run_allosmod_bmi(self):
        """Test run of final prediction"""
        j = self.make_test_job(cryptosite.Job, 'RUNNING')
        fname = os.path.join(j.directory, 'random.out')
        with open(fname, 'w') as fh:
            fh.write('42\n')
        cls = j._run_in_job_directory(j.run_allosmod_bmi)
        self.assertIsInstance(cls, saliweb.backend.SGERunner)


if __name__ == '__main__':
    unittest.main()
