#!/usr/bin/env python3

import sys
import logging
import tempfile

sys.path.insert(0, '/home/')
import inchikeyMIRIAM
import rpTool
import rpCache

logging.basicConfig(
    level=logging.DEBUG,
    #level=logging.WARNING,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S',
)

def main(input_tar,
         target_sbml,
         output_tar,
         species_group_id='central_species',
         sink_species_group_id='rp_sink_species'): 
    with tempfile.TemporaryDirectory() as tmpInputFolder:
        inchikey_enriched_target_sbml = os.path.join(tmpInputFolder, 'tmp.sbml')
        inchikeyMIRIAM.main(target_sbml, inchikey_enriched_target_sbml)
        mergeSBML_hdd(input_tar,
                      inchikey_enriched_target_sbml,
                      output_tar,
                      species_group_id,
                      sink_species_group_id)
