from flask import render_template, request, send_from_directory
import saliweb.frontend
from saliweb.frontend import get_completed_job, Parameter, FileParameter
import os
from . import submit_page

parameters = [Parameter("name", "Job name", optional=True),
              FileParameter("input_pdb", "PDB file to analyze", optional=True),
              Parameter("input_pdbid", "PDB ID (e.g. 1abc) to analyze",
                        optional=True),
              Parameter("chain",
                        "PDB chain(s) to analyze (e.g. 'A' or 'A,B')")]
app = saliweb.frontend.make_application(__name__, parameters)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/help')
def help():
    return render_template('help.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/download')
def download():
    return render_template('download.html')


@app.route('/job', methods=['GET', 'POST'])
def job():
    if request.method == 'GET':
        return saliweb.frontend.render_queue_page()
    else:
        return submit_page.handle_new_job()


@app.route('/results.cgi/<name>')  # compatibility with old perl-CGI scripts
@app.route('/job/<name>')
def results(name):
    job = get_completed_job(name, request.args.get('passwd'))
    if os.path.exists(job.get_path('cryptosite.pol.pred.pdb')):
        return saliweb.frontend.render_results_template("results_ok.html",
                                                        job=job)
    else:
        with open(job.get_path('stage.out')) as fh:
            stage = fh.readline().rstrip('\r\n')
        return saliweb.frontend.render_results_template("results_failed.html",
                                                        job=job, stage=stage)


@app.route('/job/<name>/<path:fp>')
def results_file(name, fp):
    job = get_completed_job(name, request.args.get('passwd'))
    return send_from_directory(job.directory, fp)
