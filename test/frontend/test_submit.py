import unittest
import saliweb.test
import os
from pathlib import Path
import re
import tempfile
import gzip


# Import the cryptosite frontend with mocks
cryptosite = saliweb.test.import_mocked_frontend("cryptosite", __file__,
                                                 '../../frontend')


def make_test_pdb(tmpdir):
    (tmpdir / 'xy').mkdir()
    with gzip.open(tmpdir / 'xy' / 'pdb1xyz.ent.gz', 'wt') as fh:
        fh.write("REMARK  6  TEST REMARK\n")


class Tests(saliweb.test.TestCase):
    """Check submit page"""

    def test_submit_page_uploaded(self):
        """Test submit page with uploaded PDB"""
        with tempfile.TemporaryDirectory() as tmpdir:
            incoming = os.path.join(tmpdir, 'incoming')
            os.mkdir(incoming)
            cryptosite.app.config['DIRECTORIES_INCOMING'] = incoming
            c = cryptosite.app.test_client()

            # No PDB uploaded
            rv = c.post('/job', data={'chain': 'A'})
            self.assertEqual(rv.status_code, 400)
            self.assertIn(b'No coordinate file has been submitted!', rv.data)

            # Empty uploaded PDB
            pdbf = os.path.join(tmpdir, 'test.pdb')
            with open(pdbf, 'w') as fh:
                pass
            rv = c.post('/job',
                        data={'chain': 'A', 'input_pdb': open(pdbf, 'rb')})
            self.assertEqual(rv.status_code, 400)
            self.assertIn(b'You have uploaded an empty file.', rv.data)

            # Successful submission (no email)
            with open(pdbf, 'w') as fh:
                fh.write(
                    "REMARK\n"
                    "ATOM      2  CA  ALA     1      26.711  14.576   5.091\n")
            rv = c.post('/job',
                        data={'chain': 'A', 'input_pdb': open(pdbf, 'rb')})
            self.assertEqual(rv.status_code, 200)
            r = re.compile(b'Your job has been submitted.*'
                           b'You can check on your job',
                           re.MULTILINE | re.DOTALL)
            self.assertRegex(rv.data, r)

            # Successful submission (with email)
            rv = c.post('/job',
                        data={'chain': 'A', 'email': 'test@example.com',
                              'input_pdb': open(pdbf, 'rb')})
            self.assertEqual(rv.status_code, 200)
            r = re.compile(b'Your job has been submitted.*'
                           b'You can check on your job',
                           re.MULTILINE | re.DOTALL)
            self.assertRegex(rv.data, r)

    def test_submit_page_id(self):
        """Test submit page with PDB ID"""
        with tempfile.TemporaryDirectory() as tmpdir:
            incoming = os.path.join(tmpdir, 'incoming')
            os.mkdir(incoming)
            cryptosite.app.config['DIRECTORIES_INCOMING'] = incoming

            # Make mock PDB database
            pdb_root = Path(tmpdir) / 'pdb'
            pdb_root.mkdir()
            make_test_pdb(pdb_root)
            cryptosite.app.config['PDB_ROOT'] = str(pdb_root)

            c = cryptosite.app.test_client()
            rv = c.post('/job', data={'chain': 'A', 'input_pdbid': '1xyz'})
            self.assertEqual(rv.status_code, 200)
            r = re.compile(b'Your job has been submitted.*'
                           b'You can check on your job',
                           re.MULTILINE | re.DOTALL)
            self.assertRegex(rv.data, r)

    def test_check_chain(self):
        """Test check_chain()"""
        self.assertRaises(saliweb.frontend.InputValidationError,
                          cryptosite.submit_page.check_chain, "x")
        cryptosite.submit_page.check_chain("A")
        cryptosite.submit_page.check_chain("A,B")


if __name__ == '__main__':
    unittest.main()
