import sys
sys.path.append('./SiteCrypt')
from cleaning import *
from seqConservation import *
from HydChrSSE import *
from BMIFeatureParser import *
from ResParserBMI import *
import os
from modeller import *


pdbc = sys.argv[-1]
pdb,chain = pdbc[:-1], pdbc[-1]

# --- get input PDB and sequencei

pdbloc = '/netapp/database/pdb/remediated/pdb/%s/pdb%s.ent.gz' % (pdb[1:3].lower(), pdb.lower())
os.system("cp %s ." % (pdbloc,))
# untar
os.system("gunzip pdb*.ent.gz")
os.system('mv pdb%s.ent %s.pdb' % (pdb.lower(), pdb))
'''
pdbloc = '/netapp/sali/peterc/Undrugabble/Testing/%s/%s.pdb' % (pdbc,pdb)
os.system("cp %s ." % (pdbloc,))
os.system('mv %s.org.pdb %s.pdb' % (pdb, pdb))
'''

querySeq = get_pdb_seq(pdb+'.pdb', chain)
sbjctSeq = ''


data = open('pdb_seqres.txt')
D = data.readlines()
data.close()

for x in xrange(0,len(D),2):
	h = D[x].strip().split()[0][1:]
	if h == pdb.lower() +'_'+ chain: sbjctSeq = D[x+1].strip()
'''
data = open('/netapp/sali/peterc/Undrugabble/Testing/%s/%s.fasta.txt' % (pdbc,pdb))
D = data.readlines()
data.close()

for d in D:
	if d[0]!='>': sbjctSeq += d.strip()
'''

# --- refine the structure (Modeller)
muscleAlign(querySeq, sbjctSeq, pdb, chain)
build_model(pdb, chain)


# --- extract bioinformatics features

# -- sequence conservation

output = open('test.seq','w')
output.write('>%s%sq\n' % (pdb, chain) + sbjctSeq)
output.close()
run_blast(pdb+chain)

parse_blast(pdb+chain+'.blast', pdb+chain, sbjctSeq)


# -- hydrophobicity, charge, SSEs
HydChrSSE(pdb+chain)

# --- gather residue-based BMI features
gather_features(pdb+chain)
res_parser(pdb+chain)

