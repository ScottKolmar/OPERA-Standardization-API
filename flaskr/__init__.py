from flask import Flask, request, send_file, render_template, abort
import os
import time
from flask.json import jsonify
import jinja2
from werkzeug.utils import secure_filename
import re
import glob
import sys
import csv
import pandas as pd

def create_app(test_config=None):
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 25
    app.config['UPLOAD_EXTENSIONS'] = ['txt', 'smi']

    @app.route('/', methods = ['GET', 'POST'])
    def index():
        return render_template('index.html')

    @app.route('/standardize/', methods = ['GET', 'POST'])
    def standardize():
        """
        Takes a SMILES string as argument and returns a JSON containing standardized SMILES strings.

        Parameters:
        smiles (string): SMILES string for a molecule. (Default = None)

        Returns:
        JSON

        """

        # Filter for POST requests
        if request.method == 'POST':
            pass

        else:
            
            # Start timer
            start_time = time.perf_counter()

            # Extract SMILES string
            smiles = request.args.get('smiles')

            # Find the current directory and path
            projdir = r'/app'
            projpath = os.path.normpath(projdir)

            # Define input and output file paths
            inputfilepath = os.path.normpath(os.path.join(projpath, 'temp_files', 'input.smi'))
            outputfilepath = os.path.normpath(os.path.join(projpath, 'temp_files', 'output.csv'))

            # Write SMILES as input.smi
            with open(inputfilepath, 'w') as f:
                f.write(smiles)
                f.close()

            # Run opera command with standardization
            opera_shell = '../usr/local/bin/OPERA/application/run_OPERA.sh'
            matlab_runtime = '../usr/local/MATLAB/MATLAB_Runtime/v99'
            command = f'./{opera_shell} {matlab_runtime} -s {inputfilepath} -o {outputfilepath} -st'
            os.system(command)

            # Recognize summary file name
            summaryfilepath = os.path.normpath(os.path.join(projpath, 'temp_files', 'input_Summary_file.csv'))

            # If summary file DOESN'T exist due to unstandardizable smiles
            if not summaryfilepath:
                standardized_smiles = None
            
            # If summary file DOES exist
            else:
                # Read summary file using pandas
                summary_df = pd.read_csv(summaryfilepath, header=0)
                standardized_smiles = summary_df['Canonical_QSARr']
                if smiles not in summary_df['Original_SMILES'].values:
                    standardized_smiles = None
                else:
                    standardized_smiles = summary_df['Canonical_QSARr'].iloc[0]
        
            # End Timer
            end_time = time.perf_counter()
            total_time = end_time - start_time

            # Clear temporary files
            temp_files_dir = os.path.join(projpath, 'temp_files')
            for f in os.listdir(temp_files_dir):
                if f != '.gitkeep':
                    file_path = os.path.join(projpath, 'temp_files', f)
                    os.remove(file_path)

            return jsonify({
                'success': True,
                'SMILES': smiles,
                'Standardized SMILES': standardized_smiles,
                'time': total_time
            })
        
    @app.route('/batch/standardize/', methods=['GET', 'POST'])
    def batch_standardize():

        # Filter for POST
        if request.method == 'POST':

            try:

                # Check input file for extension
                uploaded_file = request.files['file']
                filename = secure_filename(uploaded_file.filename)

                # Check if filename is empty
                if filename != '':

                    # Check file extensions
                    file_ext = filename.split('.')[1]
                    if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                        abort(400)
                    
                    # Save file as input.smi within temp_files
                    projdir = os.path.normpath(r'/app')
                    uploaded_file.save(os.path.join(projdir, 'temp_files', 'input.smi'))
            
            except:
                abort(422)
            
            # Start timer
            start_time = time.perf_counter()

            # Define input and output file paths
            inputfilepath = os.path.normpath(os.path.join(projdir, 'temp_files', 'input.smi'))
            outputfilepath = os.path.normpath(os.path.join(projdir, 'temp_files', 'output.csv'))
            descfilepath = os.path.normpath(os.path.join(projdir, 'PadelDesc.csv'))

            # Extract SMILES list
            with open(inputfilepath, 'r') as f:
                smiles_list = f.read().split('\n')

            # Fill descriptor csv with 0s
            df = pd.read_csv(descfilepath, header=0,index_col=0)
            for i in range(len(smiles_list)):
                df = df.append(pd.Series(0, index=df.columns), ignore_index=True)

            # Save descriptor csv
            df.to_csv(descfilepath)

            # Run standardization
            try:
                # Run opera command with standardization
                opera_shell = '../usr/local/bin/OPERA/application/run_OPERA.sh'
                matlab_runtime = '../usr/local/MATLAB/MATLAB_Runtime/v99'
                command = f'./{opera_shell} {matlab_runtime} -s {inputfilepath} -d {descfilepath} -o {outputfilepath} -st'
                os.system(command)
            
            except:
                abort(422)

            # Recognize summary file name
            summaryfilepath = os.path.normpath(os.path.join(projdir, 'temp_files', 'input_Summary_file.csv'))
            
            # Read structure from summary file with
            summary_df = pd.read_csv(summaryfilepath, header=0)

            # Concatenate missing structures into summary dataframe
            missing_smiles_df_list = [pd.DataFrame(data = {'Original_SMILES': [smiles], 'Canonical_QSARr': [None]}) for smiles in smiles_list if smiles not in summary_df['Original_SMILES'].values]
            if missing_smiles_df_list:
                missing_smiles_df = pd.concat([pd.DataFrame(data = {'Original_SMILES': [smiles], 'Canonical_QSARr': [None]}) for smiles in smiles_list if smiles not in summary_df['Original_SMILES'].values], ignore_index=True)
                summary_df = pd.concat([summary_df, missing_smiles_df])
            
            # Construct output dictionary
            standardized_dicts = [{'SMILES': summary_df['Original_SMILES'].iloc[i], 'standardized SMILES': summary_df['Canonical_QSARr'].iloc[i]} for i in range(len(summary_df['Original_SMILES']))]
        
            # End Timer
            end_time = time.perf_counter()
            total_time = end_time - start_time

            # Clear temporary files
            temp_files_dir = os.path.join(projdir, 'temp_files')
            for f in os.listdir(temp_files_dir):
                if f != '.gitkeep':
                    file_path = os.path.join(projdir, 'temp_files', f)
                    os.remove(file_path)

            return jsonify({
                'success': True,
                'standardizations': standardized_dicts,
                'time': total_time
            })
        
        # Filter for GET
        if request.method == 'GET':

            # Return file upload template if no smiles argument
            if not request.args.get('smiles'):
                return render_template('batch_standardize.html')
            
            # Start timer
            start_time = time.perf_counter()

            # Define project path
            projpath = os.path.normpath(r'/app')

            # Define input and out file paths
            inputfilepath = os.path.normpath(os.path.join(projpath, 'temp_files', 'input.smi'))
            outputfilepath = os.path.normpath(os.path.join(projpath, 'temp_files', 'output.csv'))
            descfilepath = os.path.normpath(os.path.join(projpath, 'PadelDesc.csv'))

            # Extract SMILES string
            smiles = request.args.get('smiles')
            smiles_list = re.split(',|\n| |\t', smiles)

            # Write SMILES as input.smi
            with open(inputfilepath, 'w') as f:
                for smiles in smiles_list:
                    f.write(smiles)
                    f.write('\n')
                f.close()
            
            # Fill descriptor csv with 0s
            df = pd.read_csv(descfilepath, header=0,index_col=0)
            for i in range(len(smiles_list)):
                df = df.append(pd.Series(0, index=df.columns), ignore_index=True)

            # Save descriptor csv
            df.to_csv(descfilepath)
            
            try:
                # Run opera command with standardization
                opera_shell = '../usr/local/bin/OPERA/application/run_OPERA.sh'
                matlab_runtime = '../usr/local/MATLAB/MATLAB_Runtime/v99'
                command = f'./{opera_shell} {matlab_runtime} -s {inputfilepath} -d {descfilepath} -o {outputfilepath} -st'
                os.system(command)
            
            except:
                abort(422)
            
            # Recognize summary file name
            summaryfilepath = os.path.normpath(os.path.join(projpath, 'temp_files', 'input_Summary_file.csv'))

            # Read structure from summary file with
            summary_df = pd.read_csv(summaryfilepath, header=0)

            # Concatenate missing structures into summary dataframe
            missing_smiles_df_list = [pd.DataFrame(data = {'Original_SMILES': [smiles], 'Canonical_QSARr': [None]}) for smiles in smiles_list if smiles not in summary_df['Original_SMILES'].values]
            if missing_smiles_df_list:
                missing_smiles_df = pd.concat([pd.DataFrame(data = {'Original_SMILES': [smiles], 'Canonical_QSARr': [None]}) for smiles in smiles_list if smiles not in summary_df['Original_SMILES'].values], ignore_index=True)
                summary_df = pd.concat([summary_df, missing_smiles_df])
            
            # Construct output dictionary
            standardized_dicts = [{'SMILES': summary_df['Original_SMILES'].iloc[i], 'standardized SMILES': summary_df['Canonical_QSARr'].iloc[i]} for i in range(len(summary_df['Original_SMILES']))]
        
            # End Timer
            end_time = time.perf_counter()
            total_time = end_time - start_time

            # Clear temporary files
            temp_files_dir = os.path.join(projpath, 'temp_files')
            for f in os.listdir(temp_files_dir):
                if f != '.gitkeep':
                    file_path = os.path.join(projpath, 'temp_files', f)
                    os.remove(file_path)

            return jsonify({
                'success': True,
                'standardizations': standardized_dicts,
                'time': total_time
            })

    # Error Handlers
    @app.errorhandler(400)
    def unprocessable_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400

    @app.errorhandler(404)
    def unprocessable_request(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource Not Found"
        }), 404

    @app.errorhandler(422)
    def unprocessable_request(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable Request"
        }), 422

    @app.errorhandler(500)
    def unprocessable_request(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Server Error"
        }), 500
                
    return app
