import saliweb.backend
import logging, os
from random import randint,choice
import string, re
import subprocess


class Job(saliweb.backend.Job):

    runnercls = saliweb.backend.SGERunner

    def run(self):

        if 'stage.out' in os.listdir('.'): 
            data = open('stage.out')
            D = data.readlines()
            data.close()
            stage = D[0].strip()

            ### - set random number
            outran= open('random.out')
            rfil = outran.read().strip()
            outran.close()


            if stage=="pre-AllosMod": 
                
                os.system('zip -r %s.zip XXX' % rfil)
                ### - submit to AllosMod
                r = saliweb.backend.SaliWebServiceRunner('http://modbase.compbio.ucsf.edu/allosmod/job',
                                 ['name=%s' % rfil, 'jobemail=peterc@salilab.org', 'zip=@%s.zip' % rfil])
                out = open('stage.out','w')
                out.write('AllosMod')
                out.close()
                return r

            elif stage=='AllosMod':
                
                self.logger.info("Post-processing AllosMod results -bmi")
                
                ### - setup the SGE script #1
                script = """
export TMPDIR=/scratch
export MYTMP=`mktemp -d`
cd $MYTMP

TT=%s
ARRAY=(/scrapp/$TT/pred_dECALCrAS1000/*)
DRIN=${ARRAY[$SGE_TASK_ID - 1]}
DIN=`echo ${DRIN} | cut -d '/' -f 5`
DROUT=`echo ${DRIN} | cut -d '/' -f 4,5`
DRT="./$DROUT"
mkdir -p $DRT
PDB=`echo $DIN | cut -d \. -f 1`



echo $ARRAY
echo $DRIN
echo $DROUT
echo $DRT
echo $PDB


module load cryptosite
cp -r /netapp/sali/peterc/cryptosite/src_multichain/analysis/for_peter/* .
cp $DRIN/pm.pdb.B*.pdb $DRIN/$PDB_mdl.pdb .

wc *.pdb

cp /netapp/sali/peterc/cryptosite/src_multichain/AM_BMI.py .
cp /netapp/sali/peterc/cryptosite/src_multichain/CHASA.py .

cryptosite soap

cat SnapList.txt


sleep 20

## - pockets
cryptosite pockets


mkdir -p /scrapp/AM/$TT/$DROUT

cp pockets.out /scrapp/AM/$TT/$DROUT

sleep 20



## - AM features
cryptosite am_bmi


cp am_features.out /scrapp/AM/$TT/$DROUT


## - copy energy.dat
ls -l

pwd

cp $DRIN/* $DRT/

echo "AM ANALYSIS"
pwd
echo "./pred_dECALCrAS1000" > list
bash /netapp/sali/peterc/cryptosite/src_multichain/analysis/allosmod_analysis.sh

cp $DRT/*.dat /scrapp/AM/$TT/$DROUT

cat check_runs.out


ls -l

rm -rf $MYTMP
date
""" % (rfil,)
            
                r = self.runnercls(script)
		r.set_sge_options('-l arch=linux-x64 -l scratch=2G -l mem_free=6G -t 1-25')
                self.logger.info("Calculated pockets for AllosMod results")

                out = open('stage.out','w')
                out.write('AllosMod-bmi')
                out.close()

                return r


            elif stage=='AllosMod-bmi':

                self.logger.info("Applying SVM model")

                ### - setup the SGE script #1
                script = """
module load sali-libraries
export PYTHONPATH="/netapp/sali/peterc/lib64/python"

python PREDICTER.py %s

date""" % ('XXX','XXX','XXX')

                r = self.runnercls(script)
                r.set_sge_options('-l arch=linux-x64 -l scratch=2G -l mem_free=2G')

                self.logger.info("Prediction DONE!")

                out = open('stage.out','w')
                out.write('DONE')
                out.close()

                return r


        else: 
            ### - set logging file
            self.logger.setLevel(logging.INFO)
            self.logger.info("Beginning preprocess() for job %s " %self.name)

            with open('param.txt') as params_file:
                pdb_file, chainid = [i.strip() for i in params_file.readlines()]

            ### - set random number
            rint = randint(100,999)
            rfil = ''.join([choice(string.letters) for nl in range(3)])+'%3i' % (rint,)
            outran= open('random.out','w')
            outran.write(rfil)
            outran.close()

            ### - setup the SGE script #1
            script = """
ls -lt

pwd

echo "working on"

module load cryptosite

cryptosite setup --short %s %s

# Put AllosMod outputs on /scrapp
echo "SCRAPP=True" >> XXX/input.dat

echo "pre-AllosMod" > stage.out

date

""" % (pdb_file, chainid)
        
            r = self.runnercls(script)
            r.set_sge_options('-l arch=linux-x64 -l diva1=1G -l scratch=2G -l mem_free=2G')

	    self.logger.info("Calculated bioinformatics features for job: %s" % rfil)
            self.logger.info("\n\nSubmitting to AllosMod")

            return r

    def postprocess(self, results=None):
        ### reschedule run
        data = open('stage.out')
        D = data.readlines()
        data.close()
        stage = D[0].strip()

        outran= open('random.out')
        rfil = outran.read().strip()
        outran.close()


        if stage=="pre-AllosMod": self.reschedule_run()
        elif stage=="AllosMod": self.reschedule_run() 
        elif stage=="AllosMod-bmi":

            ### - gather the AM data
            self.logger.info("Gathering AllosMod results")
            subprocess.check_call("module load cryptosite && cryptosite gather /scrapp/AM/%s" % rfil)

            ### - run SVM
            ## TO DELETE
            data = open('stage.out','w')
            data.write('AllosMod-bmi')
            data.close()
            ##
            self.reschedule_run()
        elif stage=="DONE":
            ### - make chimera session file
            self.logger.info("Completing the job: writing a Chimera session file.")
            os.system('cp XXX.pol.pred cryptosite.pol.pred')
            os.system('cp XXX.pol.pred.pdb cryptosite.pol.pred.pdb')
            
            data = open('script.chimerax')
            chimeraSession = data.read()
            data.close()

            (filepath, jobdir) = os.path.split(self.url)
            pdb_temp = "/cryptosite.pol.pred.pdb?"
            pdb_url = re.sub('\?', pdb_temp, jobdir)
            pdburl = filepath + "/" + pdb_url
            urlAddress = self.url

            ftr_temp = "/cryptosite.pol.pred?"
            ftr_url = re.sub('\?', ftr_temp, jobdir)
            ftrurl = filepath + "/" + ftr_url

            chimeraSession += """
open_files("%s", "%s")
]]>
</py_cmd>
</ChimeraPuppet>""" % (pdburl,ftrurl)

            out = open('cryptosite.chimerax', 'w')
            out.write(chimeraSession)
            out.close()
            self.logger.info("Job completed! Results available at: %s" % urlAddress)

            os.system('zip chimera.zip cryptosite.chimerax')

        else: 
            self.logger.info("\n\nEXITING: no stage output!")
            pass


def get_web_service(config_file):
    db = saliweb.backend.Database(Job)
    config = saliweb.backend.Config(config_file)
    return saliweb.backend.WebService(config, db)
