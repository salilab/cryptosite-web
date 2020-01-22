import saliweb.backend
import logging, os
import glob
import shutil
from random import randint,choice
import string, re
import subprocess

class Stage(object):
    """Keep track of where we are in a multi-stage job.
       The current stage of the job is stored in a file in the job directory."""

    filename = 'stage.out'

    @classmethod
    def read(cls):
        """Get the current job stage. Can be a string or None."""
        if os.path.exists(cls.filename):
            with open(cls.filename) as data:
                return data.readline().strip()

    @classmethod
    def write(cls, val):
        """Set the current job stage. Can be a string or None."""
        if val is None:
            if os.path.exists(cls.filename):
                os.unlink(cls.filename)
        else:
            with open(cls.filename, 'w') as out:
                out.write(val)


class Job(saliweb.backend.Job):

    runnercls = saliweb.backend.WyntonSGERunner

    def preprocess(self):
        # Clean up from any previous runs (e.g. a failed run being resubmitted)
        Stage.write(None)
        for f in glob.glob("sge-script*") + glob.glob("XXX*"):
            if os.path.isdir(f):
                shutil.rmtree(f, ignore_errors=True)
            else:
                os.unlink(f)

    def _set_random(self):
        """Determine and return a random file name"""
        rint = randint(100,999)
        rfil = ''.join([choice(string.ascii_letters)
                       for nl in range(3)]) + '%3i' % rint
        with open('random.out', 'w') as outran:
            outran.write(rfil)
        return rfil

    def _get_random(self):
        """Return the previously-determined random file name"""
        with open('random.out') as outran:
            return outran.read().strip()

    def run(self):
        # Determine which stage we're at
        stages = {None: self.run_first,
                  'pre-AllosMod': self.run_pre_allosmod,
                  'AllosMod': self.run_allosmod,
                  'AllosMod-bmi': self.run_allosmod_bmi}
        return stages[Stage.read()]()

    def run_pre_allosmod(self):
        rfil = self._get_random()
        subprocess.check_call(['zip', '-r', '%s.zip' % rfil, 'XXX'])
        ### - submit to AllosMod
        r = saliweb.backend.SaliWebServiceRunner(
                         'https://modbase.compbio.ucsf.edu/allosmod/job',
                         ['name=%s' % rfil, 'zip=@%s.zip' % rfil])
        Stage.write('AllosMod')
        return r

    def run_allosmod(self):
        rfil = self._get_random()
        self.logger.info("Post-processing AllosMod results -bmi")

        ### - setup the SGE script #1
        script = """
export TMPDIR=/scratch
export MYTMP=`mktemp -d`
cd $MYTMP

TT=%s
ARRAY=(/wynton/scratch/$TT/pred_dECALCrAS1000/*)
DRIN=${ARRAY[$SGE_TASK_ID - 1]}
DIN=`echo ${DRIN} | cut -d '/' -f 6`
DROUT=`echo ${DRIN} | cut -d '/' -f 5,6`
DRT="./$DROUT"
mkdir -p $DRT
PDB=`echo $DIN | cut -d \. -f 1`



echo $ARRAY
echo $DRIN
echo $DROUT
echo $DRT
echo $PDB


module load Sali
module load cryptosite
cp $DRIN/pm.pdb.B*.pdb .

wc *.pdb

cryptosite soap

cat SnapList.txt


sleep 20

## - pockets
cryptosite pockets


mkdir -p /wynton/scratch/AM/$TT/$DROUT

cp pockets.out /wynton/scratch/AM/$TT/$DROUT

sleep 20



## - AM features
cryptosite am_bmi


cp am_features.out /wynton/scratch/AM/$TT/$DROUT


## - copy energy.dat
ls -l

pwd

cp $DRIN/* $DRT/

echo "AM ANALYSIS"
pwd
cryptosite analysis ./pred_dECALCrAS1000

cp $DRT/*.dat /wynton/scratch/AM/$TT/$DROUT

cat check_runs.out


ls -l

rm -rf $MYTMP
date
""" % (rfil,)

        r = self.runnercls(script)
        r.set_sge_options('-l arch=lx-amd64 -l scratch=2G -l mem_free=6G -t 1-25')
        self.logger.info("Calculated pockets for AllosMod results")

        Stage.write('AllosMod-bmi')
        return r


    def run_allosmod_bmi(self):
        self.logger.info("Applying SVM model")

        ### - setup the SGE script #1
        script = """
module load Sali
module load cryptosite
cryptosite predict XXX
date"""

        r = self.runnercls(script)
        r.set_sge_options('-l arch=lx-amd64 -l scratch=2G -l mem_free=2G')

        self.logger.info("Prediction DONE!")

        Stage.write('DONE')

        return r

    def run_first(self):
        ### - set logging file
        self.logger.setLevel(logging.INFO)
        self.logger.info("Beginning preprocess() for job %s " %self.name)

        with open('param.txt') as params_file:
            pdb_file, chainid = [i.strip() for i in params_file.readlines()]

        ### - set random number
        rfil = self._set_random()

        ### - setup the SGE script #1
        script = """
ls -lt

pwd

echo "working on"

module load Sali
module load cryptosite

cryptosite setup --short %s %s >& setup.log

# Put AllosMod outputs on /wynton/scratch
echo "SCRAPP=True" >> XXX/input.dat

echo "pre-AllosMod" > stage.out

date

""" % (pdb_file, chainid)

        r = self.runnercls(script)
        r.set_sge_options('-l arch=lx-amd64 -l scratch=2G -l mem_free=2G')

        self.logger.info("Calculated bioinformatics features for job: %s" % rfil)
        self.logger.info("Submitting to AllosMod")
        return r

    def postprocess(self, results=None):
        stages = {'pre-AllosMod': self.postprocess_first,
                  'AllosMod': self.reschedule_run,
                  'AllosMod-bmi': self.postprocess_allosmod_bmi,
                  'DONE': self.postprocess_final}
        return stages[Stage.read()]()

    def postprocess_first(self):
        """Check errors from initial setup"""
        with open('setup.log') as fh:
            contents = fh.read()
        # Return on user errors (job will complete)
        if 'chains were not found' in contents \
           or 'file contains the following invalid residue types' in contents:
            return
        # No errors -> continue to next stage
        self.reschedule_run()

    def postprocess_allosmod_bmi(self):
        """Gather results from processing AllosMod output"""
        rfil = self._get_random()

        ### - gather the AM data
        self.logger.info("Gathering AllosMod results")
        subprocess.check_call(". /etc/profile && "
                              "module load cryptosite && "
                              "cryptosite gather /wynton/scratch/AM/%s "
                              ">& gather.out" % rfil,
                              shell=True)

        ### - run SVM
        ## TO DELETE
        Stage.write('AllosMod-bmi')
        ##
        self.reschedule_run()

    def postprocess_final(self):
        ### - make chimera session file
        self.logger.info("Completing the job: writing a Chimera session file.")
        shutil.copy('XXX.pol.pred', 'cryptosite.pol.pred')
        shutil.copy('XXX.pol.pred.pdb', 'cryptosite.pol.pred.pdb')

        (filepath, jobdir) = os.path.split(self.url)
        pdb_temp = "/cryptosite.pol.pred.pdb?"
        pdb_url = re.sub('\?', pdb_temp, jobdir)
        pdburl = filepath + "/" + pdb_url
        urlAddress = self.url

        ftr_temp = "/cryptosite.pol.pred?"
        ftr_url = re.sub('\?', ftr_temp, jobdir)
        ftrurl = filepath + "/" + ftr_url

        subprocess.check_call(". /etc/profile && "
                              "module load cryptosite && "
                              "cryptosite chimera %s %s cryptosite.chimerax"
                              % (pdburl, ftrurl), shell=True)

        self.logger.info("Job completed! Results available at: %s" % urlAddress)
        subprocess.check_call(['zip', 'chimera.zip', 'cryptosite.chimerax'])

def get_web_service(config_file):
    db = saliweb.backend.Database(Job)
    config = saliweb.backend.Config(config_file)
    return saliweb.backend.WebService(config, db)
