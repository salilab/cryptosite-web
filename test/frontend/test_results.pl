use saliweb::Test;
use Test::More 'no_plan';
use Test::Exception;
use File::Temp qw(tempdir);

BEGIN {
    use_ok('cryptosite');
}

my $t = new saliweb::Test('cryptosite');

# Check results page

# Check display_ok_job
{
    my $frontend = $t->make_frontend();
    my $job = new saliweb::frontend::CompletedJob($frontend,
                        {name=>'testjob', passwd=>'foo', directory=>'/foo/bar',
                         archive_time=>'2009-01-01 08:45:00'});
    my $ret = $frontend->display_ok_job($frontend->{CGI}, $job);
    like($ret, '/Job.*testjob.*has completed.*chimera\.zip.*' .
               'UCSF Chimera session file/ms', 'display_ok_job');
}

# Check display_failed_job at DONE stage
{
    my $frontend = $t->make_frontend();
    my $job = new saliweb::frontend::CompletedJob($frontend,
                        {name=>'testjob', passwd=>'foo', directory=>'/foo/bar',
                         archive_time=>'2009-01-01 08:45:00'});
    my $ret = $frontend->display_failed_job($frontend->{CGI}, $job, "DONE");
    like($ret, '/Your CryptoSite job.*testjob.*failed to produce any ' .
               'prediction.*' .
               'please see the.*#errors.*help page.*For more information, ' .
               'you can.*framework\.log.*download the CryptoSite file\-check ' .
               'log file.*' .
               'contact us/ms',
         'display_failed_job_done');
}

# Check display_failed_job at setup stage
{
    my $frontend = $t->make_frontend();
    my $job = new saliweb::frontend::CompletedJob($frontend,
                        {name=>'testjob', passwd=>'foo', directory=>'/foo/bar',
                         archive_time=>'2009-01-01 08:45:00'});
    my $ret = $frontend->display_failed_job($frontend->{CGI}, $job,
                                            "pre-AllosMod");
    like($ret, '/Your CryptoSite job.*testjob.*failed to produce any ' .
               'prediction.*' .
               'please see the.*#errors.*help page.*For more information, ' .
               'you can.*setup\.log.*download the CryptoSite setup ' .
               'log file.*' .
               'contact us/ms',
         'display_failed_job_setup');
}

# Check get_results_page
{
    my $frontend = $t->make_frontend();
    my $job = new saliweb::frontend::CompletedJob($frontend,
                        {name=>'testjob', passwd=>'foo', directory=>'/foo/bar',
                         archive_time=>'2009-01-01 08:45:00'});
    my $tmpdir = tempdir(CLEANUP=>1);
    ok(chdir($tmpdir), "chdir into tempdir");

    ok(open(FH, "> stage.out"), "Open stage.out");
    print FH "DONE\n";
    ok(close(FH), "Close stage.out");

    my $ret = $frontend->get_results_page($job);
    like($ret,
         '/Your CryptoSite job.*testjob.*failed to produce any prediction/',
         'get_results_page (failed job)');

    ok(open(FH, "> cryptosite.pol.pred.pdb"), "Open cryptosite.pol.pred.pdb");
    ok(close(FH), "Close cryptosite.pol.pred.pdb");

    $ret = $frontend->get_results_page($job);
    like($ret, '/Job.*testjob.*has completed/',
         '                 (successful job)');

    chdir("/");
}
