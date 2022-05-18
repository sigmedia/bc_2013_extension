package SENTWER;

#compute the WER with dynamic programming by comparing two input string
#this is not suitable for long text alingment because of efficiency problme of perl
#the return will include WER, insertions, deletions and substitutions
#format should be (test, ref)
sub sent_wer
{
	
	
  (@_ == 2)|| die "ERROR: should have two input strings for WER calcuation\n";

  $SUBPEN=10;     
  $DELPEN=7;
  $INSPEN=7;
  $NIL=0, $DIAG=1, $HOR=2, $VERT=3;
  $NULLC="???";

#########################
#varaibles

  #print "DEB: @_ \n";
  my $ts=shift(@_);
  my $rs=shift(@_);
  
  $ts=~s/^\s+//;
  $rs=~s/^\s+//g;
  
  my @ts=split(/\s+/, $ts);
  my @rs=split(/\s+/, $rs);
  my $tn=@ts; 
  my $rn=@rs;
  
  unshift(@ts," ");
  unshift(@rs," ");
  
  #print "DEB: ts=$ts rs=$rs tn=$tn rn=$rn\n";
  #these grids are global
  @grid_score = @grid_dir= @grid_ins= @grid_del= @grid_sub= @grid_hit=();

  
  my $pos0=0, $pos=0;    
  my $h, $d, $v;
##########################
#initialize  
  $grid_score[0]=$grid_ins[0]=$grid_del[0]=$grid_sub[0]=$grid_hit[0]=0;
  $grid_dir[0]=$NIL;
  print_cell(0,0,$rn+1);

  for (my $i=1; $i<=$tn; $i++){
  
    $pos=$i*($rn+1);
    $pos0=($i-1)*($rn+1);
    
    #print "DB: pos=$pos pos0=$pos0\n";
    
    cp_grid($pos+0, $pos0+0);
    $grid_dir[$pos+0]=$HOR;
    
    if ($ts[$i] ne $NULLC){
       #print "DB ts[$i]=$ts[$i]\n";
       $grid_score[$pos+0]+= $INSPEN;
       $grid_ins[$pos+0]++;
    }#accumulate insertion if not null
  	
    print_cell($i,0,$rn+1);
  }#init ts
  
  for (my $i=1; $i<=$rn; $i++){
  
     cp_grid($i, $i-1);
     $grid_dir[$i]=$VERT;
     
     if ($rs[$i] ne $NULLC){
        #print "DB rs[$i]=$rs[$i]\n";
        
        $grid_score[$i]	+= $DELPEN;
        $grid_del[$i]++;
     	
     }#accumulate insertion if not null
  
   print_cell(0,$i,$rn+1);	
  }#init rs
  
############################
#comparing


  for(my $i=1; $i<=$tn; $i++){
  	
  	$pos=$i*($rn+1);
  	$pos0=($i-1)*($rn+1);
  	my $testnull=($ts[$i] eq $NULLC)?1:0;
  	
  	for (my $j=1; $j<=$rn; $j++){
  	   my $refnull=($rs[$i] eq $NULLC)?1:0;
  	   
  	   if (($refnull==1) && ($testnull==1)){
  	   	$h=$grid_score[$pos0+$j];
  	   	$d=$grid_score[$pos0+$j-1];
  	   	$v=$grid_score[$pos+$j-1];
  	   	
                if (($d<=$v) && ($d<=$h)){
                	
                    cp_grid($pos+$j, $pos0+$j-1);
                    $grid_dir[$pos+$j]   =$DIAG;
                    
                }elsif ($h < $v){
                    cp_grid($pos+$j, $pos0+$j);
                    $grid_dir[$pos+$j]=$HOR;
                	
                }else{
                
                   cp_grid($pos+$j, $pos+$j-1);
                   $grid_dir[$pos+$j]=$VERT;
                
                
                
                }
  	   }#null ref & test
  	   elsif($refnull == 1){
  	   	#print "ref =NULL \n";
  	   	cp_grid($pos+$j, $pos+$j-1);
  	   	$grid_dir[$pos+$j]=$VERT;
  	   	
  	   }#ref is null
  	   elsif($testnull ==1){
  	   	#print "test =NULL \n";
  	   	cp_grid($pos+$j, $pos0+$j);
  	   	$grid_dir[$pos+$j]=$HOR;
  	   	
  	   }#test is null
  	   else{
  	   
  	     $h=$grid_score[$pos0+$j]+$INSPEN;
  	     $d=$grid_score[$pos0+$j-1];
  	     
  	     #print "ts=$ts[$i] rs=$rs[$j]\n";
  	     $d+=$SUBPEN if ($ts[$i] ne $rs[$j]);
  	     
  	     $v=$grid_score[$pos+$j-1]+$DELPEN;
  	     
  	     #print "DBG: grid: h=$h v=$v d=$d\n";
  	     
  	     
  	     if (($d<=$h) && ($d<=$v)){#dia
  	     
  	          cp_grid($pos+$j, $pos0+$j-1);
  	          $grid_score[$pos+$j]=$d;
  	          $grid_dir[$pos+$j]=$DIAG;
  	          
  	          if ($rs[$j] eq $ts[$i]){
  	          
  	            $grid_hit[$pos+$j]++;
  	          }else{
  	          
  	            $grid_sub[$pos+$j]++;
  	          }
  	          
  	          
  	     	
  	     }#dia
  	     elsif ($h < $v){
  	     	
  	       cp_grid($pos+$j, $pos0+$j);
  	       $grid_score[$pos+$j]=$h;
  	       $grid_dir[$pos+$j]=$HOR;
  	       $grid_ins[$pos+$j]++;
  	     }else{
  	       cp_grid($pos+$j, $pos+ $j-1);
  	       $grid_score[$pos+$j]=$v;
  	       $grid_dir[$pos+$j]=$VERT;
  	       $grid_del[$pos+$j]++;
  	     
  	     
  	     }
  	   
  	   
  	   }#all not null
  	
  	print_cell($i,$j,$rn+1);	
  	}#each ref cell
  	
  }#each test cell
	
	
  


#now collect the status

  $score=gridij($tn, $rn, $rn+1, @grid_score);
  $h=gridij($tn, $rn, $rn+1, @grid_hit);
  $d=gridij($tn, $rn, $rn+1, @grid_del);
  $s=gridij($tn, $rn, $rn+1, @grid_sub);
  $i=gridij($tn, $rn, $rn+1, @grid_ins);

  #print "DEB:hit=$h sub=$s del=$d ins=$i\n";
  return ($h,$d,$s,$i, $score);
}


sub cp_grid()
{

  my $pos1=shift;
  my $pos2=shift;
  
  #print "DB:cp_grid: pos1=$pos1 pos2=$pos2\n";
   
  $grid_score[$pos1]	=$grid_score[$pos2];
  $grid_ins[$pos1]	=$grid_ins[$pos2];
  $grid_del[$pos1]	=$grid_del[$pos2];
  $grid_sub[$pos1]	=$grid_sub[$pos2];
  $grid_hit[$pos1]	=$grid_hit[$pos2];
  $grid_dir[$pos1]      =$grid_dir[$pos2];
  	
	
}

sub print_cell()
{
	my $i=shift;
	my $j=shift;
	my $l=shift;

        my @str_name=("NIL","DIAG","HOR","VERT");
     
	
	#print "DB:=======================================\n";
	#print "DB: i=$i j=$j l=$l\n";
	#print "DB: CELL[$i,$j].score=",gridij($i,$j,$l, @grid_score),"\n";
	#print "DB: CELL[$i,$j].hit=",gridij($i,$j,$l, @grid_hit),"\n";
	#print "DB: CELL[$i,$j].del=",gridij($i,$j,$l, @grid_del),"\n";
	#print "DB: CELL[$i,$j].sub=",gridij($i,$j,$l, @grid_sub),"\n";
	
	#print "DB: CELL[$i,$j].ins=",gridij($i,$j,$l, @grid_ins),"\n";
	
	
	#print "DB: CELL[$i,$j].dir=",$str_name[gridij($i,$j,$l, @grid_dir)],"\n";
	
	#print "DB:=======================================\n";
	
	
	
}

sub gridij()
{
   my $i=shift;
   my $j=shift;
   my $len=shift;
   my @x=@_;
   
   #print "debug: @x \n";
   return  $x[$i*$len+$j];
	
}

1;