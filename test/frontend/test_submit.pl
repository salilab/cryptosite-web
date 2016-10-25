use saliweb::Test;
use Test::More 'no_plan';
use File::Temp;

BEGIN {
    use_ok('cryptosite');
}

my $t = new saliweb::Test('cryptosite');

# Check job submission

# Check get_submit_page with PDB ID
{
    my $self = $t->make_frontend();
    my $cgi = $self->cgi;

    my $tmpdir = File::Temp::tempdir(CLEANUP=>1);
    ok(chdir($tmpdir), "chdir into tempdir");
    ok(mkdir("incoming"), "mkdir incoming");
    ok(open(FH, "> test.pdb"), "Open test.pdb");
    print FH "REMARK\nATOM      2  CA  ALA     1      26.711  14.576   5.091\n";
    ok(close(FH), "Close test.pdb");
    open(FH, "test.pdb");

    $cgi->param('input_pdb', \*FH);
    $cgi->param('email', 'test@example.com');
    $cgi->param('chain', 'A');
    my $ret = $self->get_submit_page();
    like($ret, qr/Job Submitted.*You can check on your job/ms,
         "submit page HTML");


    chdir('/') # Allow the temporary directory to be deleted
}
