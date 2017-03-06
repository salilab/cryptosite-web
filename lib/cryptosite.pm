package cryptosite;
use saliweb::frontend;
use strict;

our @ISA = "saliweb::frontend";

sub new {
    return saliweb::frontend::new(@_, "##CONFIG##");
}

sub get_navigation_links {
    my $self = shift;
    my $q = $self->cgi;
    return [
        $q->a({-href=>$self->index_url}, "CryptoSite Home"),
        $q->a({-href=>$self->queue_url}, "Current Queue"),
        $q->a({-href=>$self->help_url}, "Help"),
        $q->a({-href=>$self->download_url}, "Download"),
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
<center><a href="http://www.sciencedirect.com/science/article/pii/S0022283616000851">
<b>P. Cimermancic et al., <i>JMB</i>, 2016</b></a>
</center>
</div>
FOOTER

}

sub get_index_page {
    my $self = shift;
    my $q = $self->cgi;
    my $download = $self->download_url;

    my $greeting = <<GREETING;
<p>CryptoSite is a computational tool for predicting the location of cryptic binding sites in proteins and protein complexes. Please read our <a href="http://www.sciencedirect.com/science/article/pii/S0022283616000851">
<b>paper</b></a> for more info.<br></br>

   The use of CryptoSite is limited to a chain of a PDB file per user per day. If you require more access or if you want to run CryptoSite in a multi-chain mode, 
   you can <a href="$download">download the source code</a> and run the
   algorithm on your own compute cluster.<br></br>
   <b>Caveat Emptor!</b> CryptoSite is freely available in the hope that it will be useful, but you must use
   it at your own risk. We make no guarantees about data confidentiality on this public service website.
   If you need to work with confidential data, you can
   <a href="$download">run CryptoSite on your own machine.</a>.
<br />&nbsp;</p>
GREETING

    return "<div id=\"resulttable\">\n" .
           $q->h2({-align=>"center"},
                  "CryptoSite: Predicting Cryptic Binding Sites") .
           $q->start_form({-name=>"mist_form", -method=>"post",
                           -action=>$self->submit_url}) .

           $q->table(

               $q->Tr($q->td({-colspan=>3}, $greeting)) .

               $q->Tr($q->td("Email address (optional)",
                      $self->help_link("email"), $q->br),
                      $q->td($q->textfield({-name=>"email",
                                            -value=>$self->email,
                                            -size=>"25"}))) .  


               $q->Tr($q->td($q->h3("PDB ID"),
                      $self->help_link("input_pdb"), $q->br),
                      $q->td([$q->textfield({-name=>'input_pdbid', 
                                                                -maxlength => 8, -size => 8,
                                                                -placeholder=>"eg. 2f6v"}) . 

                                  $q->h3('or') . ' upload file: ' . $q->filefield({-name=>'input_pdb',
                                                                               -size => 10})])) .



               $q->Tr($q->td("Chain ID",
                      $self->help_link("chain"), $q->br),
                      $q->td($q->textfield({-name=>"chain",
                                            -placeholder=>"eg. A",
                                            -size=>"8"}))) .

               $q->Tr($q->td("Name your job"),
                      $q->td($q->textfield({-name=>"name",
                                            -placeholder=>"2f6vA", -size=>"8"}))) .

               $q->Tr($q->td({-colspan=>"2"}, "<center>" .
                      $q->input({-type=>"submit", -value=>"Process"}) .
                      $q->input({-type=>"reset", -value=>"Reset"}) .
                             "</center><p>&nbsp;</p>"))) .
           $q->end_form .
           "</div>\n";

}

sub get_submit_page {
    my $self = shift;
    my $q = $self->cgi;

    my $user_pdbid    = lc $q->param('input_pdbid')||""; 
    my $user_name     = $q->param('name')||"";       
    my $email         = $q->param('email')||"";      
    my $chain         = $q->param('chain')||"";      

    check_optional_email($email);
    #check_pdb_name($user_pdbid);
    check_chain($chain);

    my $job = $self->make_job($user_name);
    my $jobdir = $job->directory;

    my $pdb_input = "";

    if(length $user_pdbid > 0) {
        $pdb_input = get_pdb_chains($self, $user_pdbid, $jobdir);
                               }
    else {
        my $user_pdb_file = $q->upload('input_pdb');   
        
        if (!$user_pdb_file) {
             throw saliweb::frontend::InputValidationError(
                       "No coordinate file has been submitted!");
          }


        ### write pdb input
        $pdb_input = "input.pdb";
        my $pdb_fname = $jobdir . "/input.pdb";
        open(INPDB, "> $pdb_fname")
          or throw saliweb::frontend::InternalError("Cannot open $pdb_fname $!");
        my $file_contents = "";
        while (<$user_pdb_file>) {
            $file_contents .= $_;
        }
        print INPDB $file_contents;
        close INPDB
           or throw saliweb::frontend::InternalError("Cannot close $pdb_fname $!");

        my $filesize = -s $pdb_fname;
        if($filesize == 0) {
           throw saliweb::frontend::InputValidationError("You have uploaded an empty file.");
                           }

         }


    ### write parameters
    my $input_param = $jobdir . "/param.txt";
    open(INPARAM, "> $input_param")
       or throw saliweb::frontend::InternalError("Cannot open $input_param: $!");
    print INPARAM "$pdb_input\n";
    print INPARAM "$chain\n";
    close INPARAM
       or throw saliweb::frontend::InternalError("Cannot close $input_param: $!");

    $job->submit($email);

    my $return=
      $q->h1("Job Submitted") .
      $q->hr .
      $q->p("Your job has been submitted to the server! " .
            "Your job ID is " . $job->name . ".") .
      $q->p("Results will be found at <a href=\"" .
            $job->results_url . "\">this link</a>.");
    if ($email) {
        $return.=$q->p("You will be notified at $email when job results " .
                       "are available.");
    }
    $return .=
      $q->p("You can check on your job at the " .
            "<a href=\"" . $self->queue_url .
            "\">CryptoSite queue status page</a>.").
      $q->p("The estimated execution time is ~1-2 days, depending on the load.").
      $q->p("If you experience a problem or you do not receive the results " .
            "for more than 5 days, please <a href=\"" .
            $self->contact_url . "\">contact us</a>.") .
      $q->p("Thank you for using our server and good luck in your research!").
      $q->p("Peter Cimermancic");

    return $return;

}

sub get_download_page {
    return <<TEXT;
<h2>Running CryptoSite locally</h2>

<p>If you want to run CryptoSite with larger systems, or with confidential
data, or you want more control over each step in the algorithm, you can
<a href="https://github.com/salilab/cryptosite/">download the source code
from GitHub</a> and run it on your own compute cluster.</p>

<p>The source code for this web service is also
<a href="https://github.com/salilab/cryptosite-web/">available at GitHub</a>.
</p>
TEXT
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








sub get_pdb_chains {
  my $self = shift;
  my $pdb_code = shift;
  my $jobdir = shift;

  my $pdb_file_name = "pdb" . $pdb_code . ".ent";
  my $full_path_pdb_file_name = saliweb::frontend::get_pdb_code($pdb_code, $jobdir);
  return $pdb_file_name;
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


