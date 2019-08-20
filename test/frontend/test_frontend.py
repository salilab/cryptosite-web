import unittest
import saliweb.test

# Import the cryptosite frontend with mocks
cryptosite = saliweb.test.import_mocked_frontend("cryptosite", __file__,
                                                 '../../frontend')


class Tests(saliweb.test.TestCase):

    def test_index(self):
        """Test index page"""
        c = cryptosite.app.test_client()
        rv = c.get('/')
        self.assertIn('CryptoSite is freely available', rv.data)

    def test_contact(self):
        """Test contact page"""
        c = cryptosite.app.test_client()
        rv = c.get('/contact')
        self.assertIn('Please address inquiries to', rv.data)

    def test_help(self):
        """Test help page"""
        c = cryptosite.app.test_client()
        rv = c.get('/help')
        self.assertIn('Output file in simple text format', rv.data)

    def test_download(self):
        """Test download page"""
        c = cryptosite.app.test_client()
        rv = c.get('/download')
        self.assertIn('run CryptoSite with larger systems', rv.data)

    def test_queue(self):
        """Test queue page"""
        c = cryptosite.app.test_client()
        rv = c.get('/job')
        self.assertIn('No pending or running jobs', rv.data)


if __name__ == '__main__':
    unittest.main()
