import unittest
import re
import saliweb.test

# Import the cryptosite frontend with mocks
cryptosite = saliweb.test.import_mocked_frontend("cryptosite", __file__,
                                                 '../../frontend')


class Tests(saliweb.test.TestCase):

    def test_results_file(self):
        """Test download of results files"""
        with saliweb.test.make_frontend_job('testjob') as j:
            j.make_file('test.log')
            c = cryptosite.app.test_client()
            rv = c.get('/job/testjob/test.log?passwd=%s' % j.passwd)
            self.assertEqual(rv.status_code, 200)

    def test_ok_job(self):
        """Test display of OK job"""
        with saliweb.test.make_frontend_job('testjob2') as j:
            j.make_file("cryptosite.pol.pred.pdb")
            c = cryptosite.app.test_client()
            for endpoint in ('job', 'results.cgi'):
                rv = c.get('/%s/testjob2?passwd=%s' % (endpoint, j.passwd))
                r = re.compile('Job.*testjob2.*has completed.*chimera\.zip.*'
                               'UCSF Chimera session file',
                               re.MULTILINE | re.DOTALL)
                self.assertRegexpMatches(rv.data, r)

    def test_failed_job_done(self):
        """Test display of job failed at DONE stage"""
        with saliweb.test.make_frontend_job('testjob3') as j:
            j.make_file("stage.out", "DONE\n\n")
            c = cryptosite.app.test_client()
            rv = c.get('/job/testjob3?passwd=%s' % j.passwd)
            r = re.compile(
                'Your CryptoSite job.*testjob3.*failed to produce any '
                'prediction.*'
                'please see the.*#errors.*help page.*For more information, '
                'you can.*framework\.log.*download the CryptoSite file\-check '
                'log file.*contact us', re.MULTILINE | re.DOTALL)
            self.assertRegexpMatches(rv.data, r)

    def test_failed_job_setup(self):
        """Test display of job failed at setup stage"""
        with saliweb.test.make_frontend_job('testjob4') as j:
            j.make_file("stage.out", "pre-AllosMod\n")
            c = cryptosite.app.test_client()
            rv = c.get('/job/testjob4?passwd=%s' % j.passwd)
            r = re.compile(
                'Your CryptoSite job.*testjob.*failed to produce any '
                'prediction.*'
                'please see the.*#errors.*help page.*For more information, '
                'you can.*setup\.log.*download the CryptoSite setup '
                'log file.*contact us', re.MULTILINE | re.DOTALL)
            self.assertRegexpMatches(rv.data, r)


if __name__ == '__main__':
    unittest.main()
