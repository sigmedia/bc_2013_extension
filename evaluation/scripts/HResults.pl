#!/usr/bin/perl
##################################################################
#calculate WER for blizard response file
#dwang2
##################################################################
use SENTWER;
##################################################################
#configure part
$auto_correction_acc_threshold = 0.90;
##################################################################
#global variables
%vlist    = ();
%refvlist = ();
%equlist  = ();
%rsent    = ();

@thead = ();
$rn    = $tn = 0;
$FT;      #test file
$FRES;    #result file
##################################################################

( @ARGV >= 3 )
  || die
"usage $0 <reference file> <response file> <result file> [dict] [equal-pair file]\n";

$ref_fn    = $ARGV[0];
$test_fn   = $ARGV[1];
$result_fn = $ARGV[2];
$dict_fn   = ( @ARGV >= 4 ) ? $ARGV[3] : "";
$equ_fn    = ( @ARGV >= 5 ) ? $ARGV[4] : "";

read_dict_file($dict_fn);
read_equ_file($equ_fn);

$FRES = open_result_file($result_fn);
$rn   = read_ref_file($ref_fn);

##################################################################
#this for debugging
#test();
##################################################################

#print_ref();
@thead = read_test_file_head($test_fn);

$tn = @thead;

#print_test_file_head();
$FT = pop(@thead);
$tn = @thead;

#print "DBG: ", %refvlist,"\n";
#print "DBG: ", %vlist,"\n";

#for all average
$a_h = $a_d = $a_s = $a_ii = 0;

#read each line in the test file
#calculate the WER
while (<$FT>) {

    #print $_;

    chomp;
    @ln = split( /\|/, $_ );

    @tnx = ();

    $p_h = $p_d = $p_s = $p_ii = 0;

    for ( $i = 0 ; $i < $tn ; $i++ ) {

        #print "DBG: time $i $ln[$i]\n";
        if ( !defined( $rsent{ $thead[$i] } ) || ( $ln[$i] =~ /^\s*NULL\s*$/ ) )
        {

            push( @tnx, $ln[$i] );
        }
        else {

            $rsent  = $rsent{ $thead[$i] };
            @tsents = preprocess_sent( $ln[$i], $rsent );

            $least_wer = 10000;
            $l_h       = $l_d = $l_s = $l_ii = 0;
            $l_sent    = "";

            print "REF SENT: $rsent \n";

            foreach $t_tsent (@tsents) {
                ( $h, $d, $s, $ii, $score ) =
                  SENTWER::sent_wer( $t_tsent, $rsent );
                $wer =
                  1 - ( ( $h + $d + $s ) == 0
                    ? 0
                    : ( $h - $ii ) / ( $h + $d + $s ) );

                # if (@tsents>1){
                #   print "   --TEST SENT: $t_tsent \n";
                #   print "   --hit=$h del=$d insert=$ii sub=$s wer=$wer\n";
                # }
                if ( $wer < $least_wer ) {
                    $least_wer = $wer;
                    $l_h       = $h;
                    $l_d       = $d;
                    $l_ii      = $ii;
                    $l_s       = $s;
                    $l_sent    = $t_tsent;

                }

            }

            $p_h += $l_h;
            $p_d += $l_d;
            $p_s = $l_s;
            $p_ii += $l_ii;
            $a_h  += $l_h;
            $a_d  += $l_d;
            $a_s = $l_s;
            $a_ii += $l_ii;

            print "BEST TEST SENT: $l_sent \n";
            print
"BEST STATISTIC: hit=$l_h del=$l_d insert=$l_ii sub=$l_s wer=$least_wer\n\n";

            push( @tnx, sprintf( "%3.3lf", $least_wer ) );

        }    #is sentence need to cal acc

        #print "DBG: time $i $tnx[$i]\n";

    }    #each filed

    #join together and output

    $ll = join( '|', @tnx );

    print $FRES $ll, "\n";

    $p_wer =
      1 - ( ( $p_h + $p_d + $p_s ) == 0
        ? 0
        : ( $p_h - $p_ii ) / ( $p_h + $p_d + $p_s ) );
    print "\n-------PERSON------\n";
    print
"PERSON STATISTIC: hit=$p_h del=$p_d insert=$p_ii sub=$p_s  wer=$p_wer \n";
    print "-------PERSON------\n\n";

}    #each line

$a_wer =
  1 - ( ( $a_h + $a_d + $a_s ) == 0
    ? 0
    : ( $a_h - $a_ii ) / ( $a_h + $a_d + $a_s ) );
print
"\n\n-----------------------------TOTAL--------------------------------------\n";
print "TOTAL STATISTIC: hit=$a_h del=$a_d insert=$a_ii sub=$a_s  wer=$a_wer \n";
print
  "-----------------------------TOTAL--------------------------------------\n";

close_test_file($FT);
close_result_file($FRES);

#########################################################
#preprocessing for test sentence
#########################################################

sub preprocess_sent {

    my $sent  = shift;
    my $rsent = shift;
    my @sents = ();

    $sent  = clear_sent($sent);
    $sent  = auto_correct($sent);
    @sents = handle_compound( $sent, $rsent );
    @sents = handle_equ_pair( $rsent, @sents );

    return @sents;

}

sub handle_equ_pair {
    my $rsent = shift;
    my @sents = @_;

    my %box   = ();
    my @rwrds = split( /\s+/, $rsent );

    my $tn = @sents;

    # print "handling equ pairs..\n";
    for ( my $i = 0 ; $i < @sents ; $i++ ) {

        $box{ $sents[$i] } = 1;
    }

    for ( my $i = 0 ; $i < @sents ; $i++ ) {

        my @twrds = split( /\s+/, $sents[$i] );
        for ( my $j = 0 ; $j < @twrds ; $j++ ) {
            my $x = $twrds[$j];
            if ( defined( $equlist{$x} ) ) {
                my $y = $equlist{$x};
                if ( grep( /^$y$/, @rwrds ) ) {

                    $twrds[$j] = $y;
                    my $newsent = join( ' ', @twrds );
                    if ( !defined( $box{$newsent} ) ) {
                        $sents[$tn] = $newsent;
                        $tn++;
                        $box{$newsent} = 1;
                        # print "ADD EQU_PAIRE ($x=$y) for sent: $sents[$i]\n";
                        last;
                    }    #add in if never exist

                }    #if it's there
            }    #there is a pair

        }    #check each word in the test sentence

    }    #check each test sentence

    #add possible pair like the entry in equ-pair: "masterly master lee"

    my $tn = @sents;
    for ( my $i = 0 ; $i < @sents ; $i++ ) {

        #print "DBG: box-$i ";
        my @twrds = split( /\s+/, $sents[$i] );

        for ( my $k = 0 ; $k < @twrds - 1 ; $k++ ) {
            my $x = $twrds[$k] . $twrds[ $k + 1 ];
            if ( !defined( $equlist{$x} ) ) { next; }

            my $y = $equlist{$x};

            if ( grep( /^$y$/, @rwrds ) ) {

                $twrds[$k] = $y;
                splice( @twrds, $k + 1, 1 );
                my $newsent = join( ' ', @twrds );
                if ( !defined( $box{$newsent} ) ) {
                    $sents[$tn] = $newsent;
                    $tn++;
                    $box{$newsent} = 1;
                    # print "ADD EQU_PAIRE ($x=$y) for sent: $sents[$i]\n";
                    last;
                }    #add in if never exist

            }    #the compound word exist in the reference

        }    #examine each possible comination of a paticular sentence

    }    #each sentence in the list

    # print "equ pairs done. \n";
    return @sents;
}

sub handle_compound {
    my $sent  = shift;
    my $rsent = shift;

    # print "handling compound words ..\n";

    #print "DBG: sent= $sent rsent=$rsent\n";
    my @swrd  = split( /\s+/, $sent );
    my @rswrd = split( /\s+/, $rsent );

    my $slen  = @swrd;
    my $rslen = @rswrd;

    #make the form normalized
    $sent  = join( ' ', @swrd );
    $rsent = join( ' ', @rswrd );

    my @sent_box = ($sent);

    my $boxlen = 1;

    #first try to combine the rsent
    for ( my $i = 0 ; $i < $rslen - 1 ; $i++ ) {

        my $cmb  = $rswrd[$i] . $rswrd[ $i + 1 ];
        my $cmbr = $rswrd[$i] . " " . $rswrd[ $i + 1 ];

        #print "DBG: IN RSENT CMB: cmb=$cmb  cmbr=$cmbr\n";

        #for each in the sentence box, check if it's the combination
        for ( my $j = 0 ; $j < $boxlen ; $j++ ) {

            #remember only the first seen combination will be splitted

            if ( $sent_box[$j] =~ /^$cmb\s+/ ) {

                #replace
                $sent_box[$boxlen] = $sent_box[$j];
                $sent_box[$boxlen] =~ s/^$cmb\s+/$cmbr /;
                $boxlen++;

                #print "DBG: in rsent cmb: done from $cmb to $cmbr in j=$j\n";
                next;
            }    #at the beginning

            if ( $sent_box[$j] =~ /\s+$cmb$/ ) {

                #replace
                $sent_box[$boxlen] = $sent_box[$j];
                $sent_box[$boxlen] =~ s/\s+$cmb$/ $cmbr/;
                $boxlen++;

                #print "DBG: in rsent cmb: done from $cmb to $cmbr in j=$j\n";
                next;

            }    #in the tail

            if ( $sent_box[$j] =~ /\s+$cmb\s+/ ) {

                #replace
                $sent_box[$boxlen] = $sent_box[$j];
                $sent_box[$boxlen] =~ s/\s+$cmb\s+/ $cmbr /;
                $boxlen++;

                #print "DBG: in rsent cmb: done from $cmb to $cmbr in j=$j\n";
                next;

            }    #in the middle

        }    #each sentence in the box

    }    #each possible combination here

    #print "DBG: after r combination: $boxlen \n";
    #then try to combin the neighboring words in the list

    for ( my $j = 0 ; $j < $boxlen ; $j++ ) {

        my $s = $sent_box[$j];

        my @o = split( /\s+/, $s );

        #print "DBG: box-$j $s\n";
        for ( my $k = 0 ; $k < @o - 1 ; $k++ ) {

            my $cmb = $o[$k] . $o[ $k + 1 ];

            if ( grep( /^$cmb$/, @rswrd ) ) {

                $o[$k] = $cmb;
                splice( @o, $k + 1, 1 );
                $sent_box[$boxlen] = join( ' ', @o );

#print "DBG: add \"$sent_box[$boxlen]\" from \"$s\" because combination $cmb\n";

                $boxlen++;

                last;

            }    #is a compound word in the reference

        }    #examine each possible comination of a paticular sentence

    }    #examine each sentence in the box

    my %sent_box = ();

    foreach $x (@sent_box) { $sent_box{$x} = 1; }
    @sent_box = keys(%sent_box);

    # if ( @sent_box > 1 ) {
    #     print "========================\n";
    #     print "COMOUND WORDS: $sent ==>\n";
    #     print_array(@sent_box);
    #     print "========================\n";
    # }

    # print "compound words done.\n";
    return @sent_box;

}

sub auto_correct {
    my $sent = shift;
    my $x;

    my @o = split( /\s+/, $sent );

    # # DEBUG
    # print "auto correcting..\n";

    #print "DBG: in auto_correct: $sent \n";
    for ( my $i = 0 ; $i < @o ; $i++ ) {

        my $itm = $o[$i];

        #print "DBG: $itm ";

        #never seen this voc
        if ( ( !defined( $refvlist{$itm} ) ) && ( !defined( $vlist{$itm} ) ) ) {

            my $ex_t = expand_word($itm);
            my $ex_r = "";
            my $bval = 0.0;
            my $bwrd = "";

            #check each word in the list, find the best accurate

            foreach $x ( keys(%refvlist) ) {
                $ex_r = expand_word($x);

                ( $h, $d, $s, $ii, $score ) = SENTWER::sent_wer( $ex_t, $ex_r );

                my $acc =
                  ( ( $h + $d + $s ) == 0
                    ? 0
                    : ( $h - $ii ) / ( $h + $d + $s ) );

                if ( $acc > $bval ) {
                    $bval = $acc;
                    $bwrd = $x;

                }

            }    #each word in ref list

            if ( $bval >= $auto_correction_acc_threshold ) {

                $o[$i] = $bwrd;

                # print "$sent: $itm==>$bwrd \n";

            }
            else {

                # print "DBG: OOV:  $itm !!! $bwrd \n";

            }

        }    #if not here

        #print "\n";
    }    #each word in the line

    $sent = join( ' ', @o );

    # print "auto correction done.\n";

    return $sent;

}

sub expand_word {
    my $wrd = shift;

    my $len = length($wrd);

    my $exwrd = "";

    for ( my $i = 0 ; $i < $len - 1 ; $i++ ) {

        $exwrd .= substr( $wrd, $i, 1 ) . " ";
    }

    $exwrd .= substr( $wrd, $len - 1, 1 );

    return $exwrd;

}

#clear some marks, like ???, __, xxx
sub clear_sent {
    my $sent = shift;

    #all lower case
    $sent = lc($sent);
    $sent =~ s/^\s+//g;
    $sent =~ s/\s+$//g;

    my @o = split( /\s+/, $sent );

    for ( my $i = 0 ; $i < @o ; $i++ ) {

        $o[$i] =~ s/\W//g;

    }

    $sent = join( " ", @o );

    return $sent;
}

#########################################################
#calculate the wer
#########################################################
sub cal_in_array {
    my $rsent  = shift;
    my @tsents = @_;

    $least_wer  = 100;
    $l_h        = $l_ii = $l_s = $l_d;
    $least_sent = "";

    foreach $t_tsent (@tsents) {
        ( $h, $d, $s, $ii, $score ) = SENTWER::sent_wer( $t_tsent, $rsent );
        $wer =
          1 - ( ( $h + $d + $s ) == 0 ? 0 : ( $h - $ii ) / ( $h + $d + $s ) );

        # if ( @tsents > 1 ) {
        #     print "   --TEST SENT: $t_tsent \n";
        #     print "   --hit=$h del=$d insert=$ii sub=$s wer=$wer\n";
        # }
        if ( $wer < $least_wer ) {
            $least_wer = $wer;
            $l_h       = $h;
            $l_d       = $d;
            $l_ii      = $ii;
            $l_s       = $s;
            $l_sent    = $t_tsent;

        }

    }

#     print "BEST TEST SENT: $l_sent \n";
#     print
# "BEST STATISTIC: hit=$l_h del=$l_d insert=$l_ii sub=$l_s wer=$least_wer\n\n";

}

##########################################################
#file operations and initialization
##########################################################

sub open_result_file {
    my $rs = shift;

    open( $FRES, ">$rs" ) || die "open result file $rs failed\n";

    return $FRES;

}

sub close_result_file {

    my $FRES = shift;
    close($FRES);

}

sub read_equ_file {

    my $equfn = shift;

    if ( $equfn ne "" ) {

        open( FEQ, $equfn ) || die "open equ pair file $equfn failed\n";
        # print "reading equ pair file $equfn ..\n";
        while (<FEQ>) {

            chomp;
            next if ( ( $_ =~ /^\s*$/ ) || ( $_ =~ /^#/ ) );

            #read in pair
            my @pa = split( /\s+/, $_ );
            ( ( @pa >= 2 ) && ( @pa <= 3 ) )
              || die "wrong format in pair file $equfn\n $_";

            $pak = shift(@pa);
            $pav = join( "", @pa );

            $equlist{$pak} = $pav;
            $equlist{$pav} = $pak;
        }

        close(FEQ);

    }
    # print "reading equ pair file $equfn done\n";
    print_hash(%equlist);
}

sub read_dict_file {
    my $dict = shift;

    if ( $dict ne "" ) {
        open( FV, $dict_fn ) || die "open voc file $dict_fn failed\n";

        # print("reading dict file $dict_fn ..\n");
        while (<FV>) {
            chomp;
            $_ =~ s/\s//g;
            $vlist{$_} = 1;

        }
        close(FV);
        # print("reading dict file done.\n");

        #print "DBG: ",%vlist,"\n";
    }

}

sub read_test_file_head {
    my $test = shift;
    my @ln   = ();

    open( $FT, $test ) || die "open test file $test failed\n";
    # print "DBG: FT=", $FT, "FR=", $FRES, "\n";
    while (<$FT>) {
        chomp;
        next if ( $_ =~ /^\s*$/ );

        @ln = split( /\|/, $_ );

        #clean the head
        my $lnn = @ln;

        #print "DBG: read_test_file_head: lnn=$lnn\n";
        for ( my $i = 0 ; $i < $lnn ; $i++ ) {
            $ln[$i] =~ s/\s//g;

        }    #clean each title
        push( @ln, $FT );

        # print $_, "\n";

        print $FRES $_, "\n";

        last;

    }

    return @ln;

}

sub close_test_file {

    my $FT = shift;
    close($FT);

}

sub read_ref_file {

    my $ref = shift;

    %refvlist = ();

    #first read in the ref file
    open( FR, $ref ) || die "open reference file $ref failed\n";

    my $n = 0;

    while (<FR>) {

        chomp($_);
        next if ( $_ =~ /^\s*$/ );
        $_ =~ s/(^\s+)|(\.)//;

        my @t = split( /\s+/, $_ );

        #the format should be like the following
        #05_01 The hapless artichokes froze the mournful linchpin.
        ( @t >= 2 )
          || die "error in the reference file $ref\n error line: $_\n";
        my $k = shift(@t);
        my $v = join( ' ', @t );
        $v = clear_sent($v);

        for ( my $j = 0 ; $j < @t ; $j++ ) {

            $refvlist{ $t[$j] } = 1;
        }

        #suppose the response file will use the format "result_" as the title
        $k = "result_" . $k;

        $rsent{$k} = $v;
        $n++;

    }

    close(FR);

    return $n;
}

#####################################################
#for some debugging
#####################################################
sub print_ref {
    my $x;

    foreach $x ( keys(%rsent) ) {
        # print("DBG: $x: $rsent{$x}\n");
    }

}

sub print_test_file_head {

    for ( my $i = 0 ; $i < @thead ; $i++ ) {
        # print "DBG $i: .$thead[$i].\n";
    }
}

sub print_array {
    my $n = @_;
    my @x = @_;
    for ( my $i = 0 ; $i < $n ; $i++ ) {
        # print $x[$i], "\n";
    }
}

sub print_hash {

    my %equlist = @_;
    # print "DBG: \n";
    # foreach my $x ( keys(%equlist) ) {
    #     print "$x = $equlist{$x}\n";
    # }
    # print "\n";

}

sub test {
    $t  = "the clumsy thunder showers undid the honourary ttt referendum";
    $r  = "the clumsy thundershowers undid the honorary refer";
    @oo = preprocess_sent( $t, $r );
    cal_in_array( $r, @oo );
    die;

}
