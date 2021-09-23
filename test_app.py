import os
import unittest
import json
from werkzeug.datastructures import FileStorage
from io import BytesIO
from flaskr import create_app

class OPERAStandardizerAPITestCase(unittest.TestCase):

    def setUp(self):
        """ Define variables and setup app."""
        self.app = create_app()
        self.client = self.app.test_client

        self.good_input = {'smiles': 'CCC'}
        self.bad_input = {'smiles': 'H[SN]C'}
        self.batch_good_inputs_string = {'smiles': 'CC,CCC,CCCC,CCCCC'}
        self.batch_good_and_bad_inputs_string = {'smiles': 'CC,CCC,H[Sn]C,CCCC'}
        self.batch_file_good_inputs = os.path.normpath(os.path.join('/app', 'test_files', 'batch_file_good_inputs.smi'))
        self.batch_file_good_and_bad_inputs = os.path.normpath(os.path.join('/app', 'test_files', 'batch_file_good_and_bad_inputs.smi'))
        self.batch_file_good_and_missing_inputs = os.path.normpath(os.path.join('/app', 'test_files', 'batch_file_good_and_missing_inputs.smi'))
        self.batch_file_good_bad_and_missing_inputs = os.path.normpath(os.path.join('/app', 'test_files', 'batch_file_good_bad_and_missing_inputs.smi'))
    
    def tearDown(self):
        """ Executed after each test. """
        pass

#--------------
# TESTS
#--------------

    def test_index(self):
        """ Test for GET / """
        res = self.client().get('/')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)

#--------------
# Single Mode
#--------------
    
    def test_standardizer_good_input(self):
        """ Pass test for normal input SMILES. """
        smiles = self.good_input['smiles']
        res = self.client().get(f'/standardize/?smiles={smiles}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['successs'])
        self.assertEqual(data['SMILES'], smiles)
        self.assertEqual(data['Standardizes SMILES'], 'CCC')
    
    def test_fail_standardizer_bad_input(self):
        """ Test for failure with bad input SMILES. """
        smiles = self.bad_input['smiles']
        res = self.client().get(f'/standardize/?smiles={smiles}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 500)
        self.assertFalse(data['successs'])

#-------------------
# Batch String Mode
#-------------------
    
    def test_batch_standardizer_string_good_inputs(self):
        """ Test for batch input with a string of good comma delimited smiles. """
        smiles = self.batch_good_inputs_string['smiles']
        res = self.client().get(f'/batch/standardize/?smiles={smiles}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['successs'])
        self.assertEqual(len(data['standardizations']), 4)
        self.assertEqual(data['standardizations'][0]['SMILES'], 'CC')
        self.assertEqual(data['standardizations'][0]['standardized SMILES'], 'CC')
    
    def test_batch_standardizer_string_good_and_bad_inputs(self):
        """ Test for batch input with a string of good and one bad comma delimited smiles. """
        smiles = self.batch_good_and_bad_inputs_string['smiles']
        res = self.client().get(f'/batch/standardize/?smiles={smiles}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['successs'])
        self.assertEqual(len(data['standardizations']), 4)
        self.assertEqual(data['standardizations'][0]['SMILES'], 'CC')
        self.assertEqual(data['standardizations'][0]['standardized SMILES'], 'CC')
        self.assertEqual(data['standardizations'][2]['SMILES'], 'H[Sn]C')
        self.assertEqual(data['standardizations'][2]['standardized SMILES'], None)
    
#-------------------
# Batch File Mode
#-------------------
    def test_batch_standardizer_file_good_inputs(self):
        """ Test for batch input with a file containing good smiles. """
        data = {
            'file': (BytesIO('my file contents'),
            self.batch_file_good_inputs)
            }
        
        res = self.client().post(f'/batch/standardize/', content_type='multipart/form-data', data=data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['successs'])
        self.assertEqual(len(data['standardizations']), 4)
        self.assertEqual(data['standardizations'][0]['SMILES'], 'CC')
        self.assertEqual(data['standardizations'][0]['standardized SMILES'], 'CC')

    def test_batch_standardizer_file_good_and_bad_inputs(self):
        """ Test for batch input with a file containing good and bad smiles. """
        data = {
            'file': (BytesIO('my file contents'),
            self.batch_file_good_and_bad_inputs)
            }
        
        res = self.client().post(f'/batch/standardize/', content_type='multipart/form-data', data=data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['successs'])
        self.assertEqual(len(data['standardizations']), 4)
        self.assertEqual(data['standardizations'][0]['SMILES'], 'CC')
        self.assertEqual(data['standardizations'][0]['standardized SMILES'], 'CC')
        self.assertEqual(data['standardizations'][2]['SMILES'], 'H[Sn]C')
        self.assertEqual(data['standardizations'][2]['standardized SMILES'], None)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()