import unittest
import saliweb.test
import os
import re
import gzip


# Import the cryptosite frontend with mocks
cryptosite = saliweb.test.import_mocked_frontend("cryptosite", __file__,
                                                 '../../frontend')


def make_test_pdb(tmpdir):
    os.mkdir(os.path.join(tmpdir,  'xy'))
    fh = gzip.open(os.path.join(tmpdir, 'xy', 'pdb1xyz.ent.gz'), 'wb')
    fh.write("REMARK  6  TEST REMARK\n")
    fh.close()


class Tests(saliweb.test.TestCase):
    """Check submit page"""

    def test_submit_page_uploaded(self):
        """Test submit page with uploaded PDB"""
        incoming = saliweb.test.TempDir()
        cryptosite.app.config['DIRECTORIES_INCOMING'] = incoming.tmpdir
        c = cryptosite.app.test_client()

        # No PDB uploaded
        rv = c.post('/job', data={'chain': 'A'})
        self.assertEqual(rv.status_code, 400)
        self.assertIn('No coordinate file has been submitted!', rv.data)

        t = saliweb.test.TempDir()

        # Empty uploaded PDB
        pdbf = os.path.join(t.tmpdir, 'test.pdb')
        with open(pdbf, 'w') as fh:
            pass
        rv = c.post('/job', data={'chain': 'A', 'input_pdb': open(pdbf)})
        self.assertEqual(rv.status_code, 400)
        self.assertIn('You have uploaded an empty file.', rv.data)

        # Successful submission (no email)
        with open(pdbf, 'w') as fh:
            fh.write("REMARK\n"
                     "ATOM      2  CA  ALA     1      26.711  14.576   5.091\n")
        rv = c.post('/job', data={'chain': 'A', 'input_pdb': open(pdbf)})
        self.assertEqual(rv.status_code, 200)
        r = re.compile('Your job has been submitted.*You can check on your job',
                       re.MULTILINE | re.DOTALL)
        self.assertRegexpMatches(rv.data, r)

        # Successful submission (with email)
        rv = c.post('/job', data={'chain': 'A', 'email': 'test@example.com',
                                  'input_pdb': open(pdbf)})
        self.assertEqual(rv.status_code, 200)
        r = re.compile('Your job has been submitted.*You can check on your job',
                       re.MULTILINE | re.DOTALL)
        self.assertRegexpMatches(rv.data, r)

    def test_submit_page_id(self):
        """Test submit page with PDB ID"""
        incoming = saliweb.test.TempDir()
        cryptosite.app.config['DIRECTORIES_INCOMING'] = incoming.tmpdir

        # Make mock PDB database
        pdb_root = saliweb.test.TempDir()
        make_test_pdb(pdb_root.tmpdir)
        cryptosite.app.config['PDB_ROOT'] = pdb_root.tmpdir

        c = cryptosite.app.test_client()
        rv = c.post('/job', data={'chain': 'A', 'input_pdbid': '1xyz'})
        self.assertEqual(rv.status_code, 200)
        r = re.compile('Your job has been submitted.*You can check on your job',
                       re.MULTILINE | re.DOTALL)
        self.assertRegexpMatches(rv.data, r)

    def test_check_chain(self):
        """Test check_chain()"""
        self.assertRaises(saliweb.frontend.InputValidationError,
                          cryptosite.submit_page.check_chain, "x")
        cryptosite.submit_page.check_chain("A")
        cryptosite.submit_page.check_chain("A,B")


if __name__ == '__main__':
    unittest.main()
