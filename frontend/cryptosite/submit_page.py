from flask import request
import saliweb.frontend
import os
import re


def handle_new_job():
    user_pdbid = request.form.get("input_pdbid", "").lower()
    user_pdb_file = request.files.get("input_pdb")
    user_name = request.form.get("name", "")
    email = request.form.get("email")
    chain = request.form.get("chain", "")

    saliweb.frontend.check_email(email, required=False)
    check_chain(chain)

    job = saliweb.frontend.IncomingJob(user_name)

    pdb_input = get_pdb_input(user_pdbid, user_pdb_file, job)

    # write parameters
    with open(job.get_path('param.txt'), 'w') as fh:
        fh.write("%s\n%s\n" % (os.path.basename(pdb_input), chain))

    job.submit(email)

    # Pop up an exit page
    return saliweb.frontend.render_submit_template('submit.html', email=email,
                                                   job=job)


def get_pdb_input(user_pdbid, user_pdb_file, job):
    """Get input PDB by ID or uploaded file"""
    if user_pdbid:
        return saliweb.frontend.get_pdb_code(user_pdbid, job.directory)
    else:
        if not user_pdb_file:
            raise saliweb.frontend.InputValidationError(
                "No coordinate file has been submitted!")
        pdb_input = job.get_path('input.pdb')
        user_pdb_file.save(pdb_input)
        if os.stat(pdb_input).st_size == 0:
            raise saliweb.frontend.InputValidationError(
                "You have uploaded an empty file.")
        return pdb_input


def check_chain(chain):
    """Check for correctly-specified chain ID"""
    if not re.match(r'[A-Z](,[A-Z])*$', chain):
        raise saliweb.frontend.InputValidationError(
            "Wrong Chain ID input! Please use a single uppercase letter for "
            "a single chain input or a comma-separated set of uppercase "
            "letters for multi-chain input.")
