use saliweb::Test;
use Test::More 'no_plan';
use Test::Exception;
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

# Test check_pdb_name
{
    throws_ok { cryptosite::check_pdb_name("") }
              saliweb::frontend::InputValidationError,
              "check_pdb_name (bad name)";
    like($@, qr/No coordinate file has been submitted!/,
         "check_pdb_name (bad name, error message)");

    cryptosite::check_pdb_name("ok.pdb");
}

# Test check_chain
{
    throws_ok { cryptosite::check_chain("x") }
              saliweb::frontend::InputValidationError,
              "check_chain (bad name)";
    like($@, qr/Wrong Chain ID input!/,
         "check_chain (bad name, error message)");

    cryptosite::check_chain("A");
    cryptosite::check_chain("A,B");
}

# Test check_sequence
{
    throws_ok { cryptosite::check_sequence("x") }
              saliweb::frontend::InputValidationError,
              "check_sequence (bad name)";
    like($@, qr/Wrong Protein Sequence input!/,
         "check_sequence (bad name, error message)");

    cryptosite::check_sequence(">A\nCGV");
}
