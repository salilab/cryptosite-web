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
                          
# Test get_project_menu
{
    my $self = $t->make_frontend();
    my $txt = $self->get_project_menu();
    like($txt, qr/Developer.*Acknowledgements.*Version testversion/ms,
         'get_project_menu');
}

# Test get_footer
{
    my $self = $t->make_frontend();
    my $txt = $self->get_footer();
    like($txt, qr/P\. Cimermancic.*JMB.*2016/ms,
         'get_footer');
}

# Test get_index_page
{
    my $self = $t->make_frontend();
    my $txt = $self->get_index_page();
    like($txt, qr/CryptoSite is a computational tool/ms,
         'get_index_page');
}
