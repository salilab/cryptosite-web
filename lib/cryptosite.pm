package cryptosite;
use base qw(saliweb::frontend);
use strict;

our @ISA = "saliweb::frontend";

sub new {
    return saliweb::frontend::new(@_, @CONFIG@);
}

sub get_navigation_links {
    my $self = shift;
    my $q = $self->cgi;
    return [
        $q->a({-href=>$self->index_url}, "CryptoSite Home"),
        $q->a({-href=>$self->queue_url}, "Current Queue"),
        $q->a({-href=>$self->help_url}, "Help"),
        $q->a({-href=>$self->contact_url}, "Contact")
        ];
}

sub get_project_menu {
    my $self = shift;
    my $version = $self->version_link;
    return <<MENU;
<p>&nbsp;</p>
<p>&nbsp;</p>
<p>&nbsp;</p>
<h4><small>Author:</small></h4><p>Peter Cimermancic</p>
<h4><small>Web Developers:</small></h4>
<p>Peter Cimermancic<br />
Leon Bichmann<br />
Ben Webb<br /></p>

<h4><small>Acknowledgements:</small></h4>
<p>Patrick Weinkam
<br />Andrej Sali</p>
<p><i>Version $version</i></p>
MENU

}

sub get_footer {
    my $self = shift;
    my $htmlroot = $self->htmlroot;
    return <<FOOTER;
<div id="address">
<center><a href="https://www.dropbox.com/s/zyu6k53fekpkzub/CryptoSite_manuscript.pdf?dl=0">
<b>P. Cimermancic, P. Weinkam, et al., <i>(submitted)</i></b></a>
</center>
</div>
FOOTER

}

sub get_index_page {
    my $self = shift;
    my $q = $self->cgi;
    my $contact = $self->contact_url;

    my $greeting = <<GREETING;
<p>CryptoSite is a computational tool for predicting the location of cryptic binding sites in proteins and protein complexes.<br></br>

<font size="5" color="red">Due to the high demand, we temporarily
stopped accepting new jobs. We are working hard to optimize the speed of
the CryptoSite webserver, and will be ready for new runs by March 1st.
We apologize for the inconvenience. Thank you!</font>


<br />&nbsp;</p>
GREETING

    return "<div id=\"resulttable\">\n" .
           $q->h2({-align=>"center"},
                  "CryptoSite: Predicting Cryptic Binding Sites") .
           $q->start_form({-name=>"mist_form", -method=>"post",
                           -action=>$self->submit_url}) .

           $q->table(

               $q->Tr($q->td({-colspan=>2}, $greeting)) .

               $q->Tr($q->td("Email address (required)",
                      $self->help_link("email"), $q->br),
                      $q->td($q->textfield({-name=>"email",
                                            -value=>$self->email,
                                            -size=>"25"}))) .

               $q->Tr($q->td($q->h3("Upload PDB coordinate file (required)",
                      $self->help_link("input_pdb"), $q->br),
                      $q->td($q->filefield({-name=>"input_pdb"})))) .

                $q->Tr($q->td("Chain ID (required)",
                      $self->help_link("chain"), $q->br),
                      $q->td($q->textfield({-name=>"chain",
                                            -placeholder=>"A or A,B,C",
                                            -size=>"25"}))) .

                $q->Tr($q->td($q->h3("Enter protein sequence (required)",
                                    $self->help_link("sequence"))),
                      $q->td($q->textarea({-name=>"sequence",
                                           -placeholder=>"Please enter sequence(s) in FASTA format with ONE-CHARACTER headers matching Chain ID(s) only. For example: >A or >B",
                                           -rows=>"10", -cols=>"40"}))) .

               $q->Tr($q->td("Name your job",
                      $q->td($q->textfield({-name=>"name",
                                            -placeholder=>"1ABC", -size=>"9"})))) .

               $q->Tr($q->td({-colspan=>"2"}, "<center>" .
                      $q->input({-type=>"submit", -value=>"Process"}) .
                      $q->input({-type=>"reset", -value=>"Reset"}) .
                             "</center><p>&nbsp;</p>"))) .
           $q->end_form .
           "</div>\n";

}

sub get_submit_page {





}

sub get_results_page {
    my ($self, $job) = @_;
    my $q = $self->cgi;
    if (-f "cryptosite.pol.pred.pdb"){
        return $self->display_ok_job($q, $job);
    } else{
        return $self->display_failed_job($q, $job);
    }
}

sub display_ok_job {
   my ($self, $q, $job) = @_;
   my $return= $q->p("Job '<b>" . $job->name . "</b>' has completed.");

   $return.= $q->p("<BR>Download <a href=\"" .
          $job->get_results_file_url("cryptosite.pol.pred").("\">CryptoSite feature output.</a>") );

   $return.= $q->p("<BR>Download <a href=\"" .
          $job->get_results_file_url("cryptosite.pol.pred.pdb").("\">CryptoSite PDB output.</a>") );

   $return.= $q->p("<BR>Download <a href=\"" .
          $job->get_results_file_url("chimera.zip").("\">UCSF Chimera session file.</a>") );

   $return .= $job->get_results_available_time();

   return $return;
}

sub display_failed_job {
    my ($self, $q, $job) = @_;
    my $return= $q->p("Your CryptoSite job '<b>" . $job->name .
                      "</b>' failed to produce any prediction.");
    $return.=$q->p("This is usually caused by incorrect input files ");

    $return.=$q->p("For a discussion of some common input errors, please see " .
                   "the " .
                   $q->a({-href=>$self->help_url . "#errors"}, "help page") .
                   ".");
    $return.= $q->p("For more information, you can " .
                    "<a href=\"" . $job->get_results_file_url("framework.log") .
                    "\">download the CryptoSite file-check log file</a>." .
                    "<BR>If the problem is not clear from this log, " .
                    "please <a href=\"" .
                    $self->contact_url . "\">contact us</a> for " .
                    "further assistance.");
    return $return;
}

sub check_email{
    my ($email) = @_;
    if ($email eq "") {
        throw saliweb::frontend::InputValidationError(
                       "No email provided!");
    }
}

# Check if a PDB name was specified
sub check_pdb_name {
    my ($pdb_name) = @_;
    if (!$pdb_name) {
        throw saliweb::frontend::InputValidationError(
                       "No coordinate file has been submitted!");
    }
}

sub check_chain {
    my ($chain) = @_;
    #if ($chain eq "") {
    #    throw saliweb::frontend::InputValidationError(
    #                   "No chain identifier provided! Please use an empty space if the PDB file doesn't have one.");
    
    unless ($chain =~ m/^[A-Z]{1}+(?:,[A-Z]{1})*?$/) {
        throw saliweb::frontend::InputValidationError(
                       "Wrong Chain ID input!\n\nPlease use a single uppercase letter for a single chain input or a comma-separated set of uppercase letters for multi-chain input.");
    }
}


sub check_sequence {
    my ($sequence) = @_;
    
    unless ($sequence =~ m/^\>{1}[A-Z]{1}\n{1}/) {
        throw saliweb::frontend::InputValidationError(
                       "Wrong Protein Sequence input!\n\nPlease use a FASTA format with exactly one character (matching chain ID) in each header line.");}


}


1;


