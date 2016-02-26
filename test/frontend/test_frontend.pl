use saliweb::Test;
use Test::More 'no_plan';

BEGIN {
    use_ok('cryptosite');
}

my $t = new saliweb::Test('cryptosite');

# Test get_navigation_links
{
    my $frontend = $t->make_frontend();
    my $links = $frontend->get_navigation_links();
    isa_ok($links, 'ARRAY', 'navigation links');
    like($links->[0], qr#<a href="http://modbase/top/">CryptoSite Home</a>#,
         'Index link');
}
                          
