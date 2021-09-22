# OPERA Standardizer API
## Author
Scott Kolmar

## Description
This API uses OPERA to standardize SMILES strings. Currently, the API runs OPERAv2.7.

Documentation for the OPERA software, developed by Kamel Mansouri, can be found here:
[OPERA-documentation](https://github.com/kmansouri/OPERA)

## API Reference

The API can be accessed at the following base URL: (http://127.0.0.1:5000/)
If custom host name and port are supplied, the base URL will change accordingly.


### Endpoints

Each of the endpoints listed in the description can be accessed for predictions. For example:

#### GET '/standardize?smiles={smiles_string}'
- Standardizes the input SMILES string
- Returns: A JSON object with a Standardized SMILES key with value of the standardized SMILES string, a SMILES key with value of the input SMILES string, a timer key with value of the time elapsed in seconds, and a success key, with value True if the calculation succeeded and False if an error occurred.
- If a structure can not be standardized by OPERA, the calculation will fail and no structure will be returned.
- Example: ```curl -L http://127.0.0.1:5000/standardize?smiles=CCC```

```
{
    'success': True,
    'SMILES': 'CCC',
    'Standardized SMILES': 'CCC',
    'time': 32.1
}
```
Batch calculations can also be performed on comma delimited, tab delimited, newline delimited, and space delimited strings of SMILES strings. For example:

#### GET /batch/standardize?smiles={delimited_smiles_strings}'
- Standardizes a list of SMILES strings.
- Returns: Returns: A JSON object with a standardized key and value of a dictionary containing Standardized SMILES and input SMILES, a timer key with value of the time elapsed in seconds, and a success key, with value True if the calculation succeeded and False if an error occurred.
- Structures that can not be standardized by OPERA will be returned with a None value for 'standardized SMILES'.
- Example: ```curl -L http://127.0.0.1:5000/batch/logBCF?smiles=CCC,CCCC```

```
{
    "standardizations": [{
        'SMILES': 'CCC',
        'standardized SMILES: 'CCC'
    },
    {
        'SMILES': 'CCCC',
        'standardized SMILES: 'CCCC'
    }],
    "success": true,
    "time": 10.78
}
```

#### POST /batch/standardize/'
- Standardizes SMILES strings in an uploaded file.
- Returns: A JSON object with a standardized key and value of a dictionary containing Standardized SMILES and input SMILES, a timer key with value of the time elapsed in seconds, and a success key, with value True if the calculation succeeded and False if an error occurred.
- Structures that can not be standardized by OPERA will be returned with a None value for 'standardized SMILES'.
- Example: ```curl -F "file=@C:\Users\Administrator\OneDrive\Profile\Desktop\OPERA_dummy_calcs\multiple_input.smi" http://127.0.0.1:5000/batch/standardize/```

```
{
    "standardizations": [{
        'SMILES': 'CCC',
        'standardized SMILES: 'CCC'
    },
    {
        'SMILES': 'CCCC',
        'standardized SMILES: 'CCCC'
    }],
    "success": true,
    "time": 10.78
}
```

### Error Handling
Errors are returned in the following json format:
```
{
    'success': False,
    'error': 404,
    'message': 'Resource Not Found'
}
```
The API returns 4 types of errors:
- 400: bad request
- 404: not found
- 422: unprocessable
- 500: internal server error


