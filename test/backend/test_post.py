import unittest
import cryptosite
import saliweb.test
import saliweb.backend
import os

class Tests(saliweb.test.TestCase):
    """Test postprocessing methods"""

    def test_postprocess_final(self):
        """Test postprocess_final()"""
        j = self.make_test_job(cryptosite.Job, 'RUNNING')
        for fname in ('XXX.pol.pred', 'XXX.pol.pred.pdb', 'script.chimerax'):
            with open(os.path.join(j.directory, fname), 'w') as fh:
                fh.write('test')
        j._run_in_job_directory(j.postprocess_final)
        with open(os.path.join(j.directory, 'cryptosite.chimerax')) as fh:
            lines = fh.readlines()
        top = 'http://server/test/path/testjob'
        self.assertEqual(lines[-4],
                'open_files("%s/cryptosite.pol.pred.pdb?passwd=abc", '
                '"%s/cryptosite.pol.pred?passwd=abc")\n' % (top, top))
        for fname in ('cryptosite.chimerax', 'chimera.zip',
                      'cryptosite.pol.pred', 'cryptosite.pol.pred.pdb'):
            os.unlink(os.path.join(j.directory, fname))

if __name__ == '__main__':
    unittest.main()
