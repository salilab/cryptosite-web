import unittest
import cryptosite
import saliweb.test
import saliweb.backend
import os
import subprocess

class MockCheckCall(object):
    def __init__(self):
        self.calls = []
    def __call__(self, cmd, **keys):
        self.calls.append(cmd)

class Tests(saliweb.test.TestCase):
    """Test postprocessing methods"""

    def test_postprocess_final(self):
        """Test postprocess_final()"""
        j = self.make_test_job(cryptosite.Job, 'RUNNING')
        for fname in ('XXX.pol.pred', 'XXX.pol.pred.pdb'):
            with open(os.path.join(j.directory, fname), 'w') as fh:
                fh.write('test')

        old_check_call = subprocess.check_call
        mock_cc = MockCheckCall()
        try:
            subprocess.check_call = mock_cc
            j._run_in_job_directory(j.postprocess_final)
        finally:
            subprocess.check_call = old_check_call

        self.assertEqual(len(mock_cc.calls), 2)
        top = 'http://server/test/path/testjob'
        self.assertTrue(mock_cc.calls[0].endswith(
                   'cryptosite chimera %s/cryptosite.pol.pred.pdb?passwd=abc '
                   '%s/cryptosite.pol.pred?passwd=abc cryptosite.chimerax'
                   % (top, top)))
        self.assertEqual(mock_cc.calls[1],
                         ["zip", "chimera.zip", "cryptosite.chimerax"])
        for fname in ('cryptosite.pol.pred', 'cryptosite.pol.pred.pdb'):
            os.unlink(os.path.join(j.directory, fname))

if __name__ == '__main__':
    unittest.main()
