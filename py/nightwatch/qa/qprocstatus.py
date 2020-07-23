from .base import QA
import glob
import os
import collections

import numpy as np
import fitsio
import json


from astropy.table import Table

class QAQPROCStatus(QA):
    '''Class representing QPROC status QA, tracking success of qproc processes.
    
    Methods:
        valid_obstype(self, obstype): Given the obstype of an exposure, returns whether QAQPROCStatus is a valid QA metric. QAQPROCStatus is currently valid for all exposures.
        run(self, indir): Given path to directory containing qproc logfiles + errorcodes.txt file, returns Astropy table with QPROCStatus data.
    
    '''
    
    def __init__(self):
        self.output_type = "QPROC_STATUS"
    
    def valid_obstype(self, obstype):
        return True
    
    def run(self, indir):
        """Generates QA data for qproc logfiles; tracks which cameras exited with a nonzero exit code. Reads in data from
        errorcodes.txt file generated by nightwatch qproc.
        Returns Table object with columns:
    
        NIGHT   EXPID   CAM  SPECTRO   QPROC_EXIT 
                                       exitcode in this column
        """
        #get night, expid data
        header_file = glob.glob(os.path.join(indir, 'preproc-*.fits'))[0]
        hdr = fitsio.read_header(header_file, 'IMAGE')
        night = hdr['NIGHT']
        expid = hdr['EXPID']
        
        #get errorcodes
        jsonfile = glob.glob(os.path.join(indir, 'errorcodes-*.txt'))[0]
        with open(jsonfile, 'r') as json_file:
            errorcodes = json.load(json_file)
        
        #get qproc status data
        infiles = glob.glob(os.path.join(indir, 'qproc-*.log'))
        results = []
        
        for infile in infiles:
            dico = dict()
            
            filename = os.path.basename(infile)
            qexit = errorcodes[filename]
            spectro = int(filename[7])
            cam = filename[6].upper()
            
            dico['NIGHT'] = night
            dico['EXPID'] = expid
            dico['SPECTRO'] = spectro
            dico['CAM'] = cam
            dico['QPROC_EXIT'] = qexit
            
            results.append(collections.OrderedDict(**dico))
            
        return Table(results, names=results[0].keys())
        