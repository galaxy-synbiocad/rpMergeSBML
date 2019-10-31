#!/usr/bin/env python3

import libsbml
import argparse

import io
import tarfile

#HDD sepcific
import os
import shutil
import random
import glob
import string

import sys #exit using sys exit if any error is encountered
sys.path.insert(0, '/home/')
import rpSBML


#######################################################################
#code taken from https://gist.github.com/stuaxo/889db016e51264581b50###
#######################################################################


import traceback
import inspect
from functools import wraps
from multiprocessing import Process, Queue

class Sentinel:
    pass


def processify(func):
    '''Decorator to run a function as a process.
    Be sure that every argument and the return value
    is *pickable*.
    The created process is joined, so the code does not
    run in parallel.
    '''

    def process_generator_func(q, *args, **kwargs):
        result = None
        error = None
        it = iter(func())
        while error is None and result != Sentinel:
            try:
                result = next(it)
                error = None
            except StopIteration:
                result = Sentinel
                error = None
            except Exception:
                ex_type, ex_value, tb = sys.exc_info()
                error = ex_type, ex_value, ''.join(traceback.format_tb(tb))
                result = None
            q.put((result, error))

    def process_func(q, *args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception:
            ex_type, ex_value, tb = sys.exc_info()
            error = ex_type, ex_value, ''.join(traceback.format_tb(tb))
            result = None
        else:
            error = None

        q.put((result, error))

    def wrap_func(*args, **kwargs):
        # register original function with different name
        # in sys.modules so it is pickable
        process_func.__name__ = func.__name__ + 'processify_func'
        setattr(sys.modules[__name__], process_func.__name__, process_func)

        q = Queue()
        p = Process(target=process_func, args=[q] + list(args), kwargs=kwargs)
        p.start()
        result, error = q.get()
        p.join()

        if error:
            ex_type, ex_value, tb_str = error
            message = '%s (in subprocess)\n%s' % (str(ex_value), tb_str)
            raise ex_type(message)

        return result

    def wrap_generator_func(*args, **kwargs):
        # register original function with different name
        # in sys.modules so it is pickable
        process_generator_func.__name__ = func.__name__ + 'processify_generator_func'
        setattr(sys.modules[__name__], process_generator_func.__name__, process_generator_func)

        q = Queue()
        p = Process(target=process_generator_func, args=[q] + list(args), kwargs=kwargs)
        p.start()

        result = None
        error = None
        while error is None:
            result, error = q.get()
            if result == Sentinel:
                break
            yield result
        p.join()

        if error:
            ex_type, ex_value, tb_str = error
            message = '%s (in subprocess)\n%s' % (str(ex_value), tb_str)
            raise ex_type(message)

    @wraps(func)
    def wrapper(*args, **kwargs):
        if inspect.isgeneratorfunction(func):
            return wrap_generator_func(*args, **kwargs)
        else:
            return wrap_func(*args, **kwargs)
    return wrapper


###########################################################
################## multiprocesses run #####################
###########################################################

#hack to stop the memory leak. Indeed it seems that looping through rpFBA and the rest causes a memory leak... According to: https://github.com/opencobra/cobrapy/issues/568 there is still memory leak issues with cobrapy. looping through hundreds of models and running FBA may be the culprit


########################## use RAM ######################


##
#
#
@processify
def singleMerge_mem(member_name, rpsbml_string, inModel):
    #open one of the rp SBML files
    rpsbml = rpSBML.rpSBML(member_name, libsbml.readSBMLFromString(rpsbml_string))
    #read the input GEM sbml model
    input_rpsbml = rpSBML.rpSBML('inputMergeModel')
    input_rpsbml.readSBML(inModel)
    rpsbml.mergeModels(input_rpsbml)
    return libsbml.writeSBMLToString(input_rpsbml.document).encode('utf-8')


##
#
#
def runMerge_mem(inputTar, inModel, outputTar):
    #loop through all of them and run FBA on them
    with tarfile.open(outputTar, 'w:xz') as tf:
        with tarfile.open(inputTar, 'r:xz') as in_tf:
            for member in in_tf.getmembers():
                if not member.name=='':
                    data = singleFBA_mem(member.name, in_tf.extractfile(member).read().decode("utf-8"), inModel)
                    fiOut = io.BytesIO(data)
                    info = tarfile.TarInfo(member.name)
                    info.size = len(data)
                    tf.addfile(tarinfo=info, fileobj=fiOut)


####################### use HDD ############################


##
#
#
@processify
def singleMerge_hdd(fileName, sbml_path, inModel, tmpOutputFolder):
    rpsbml = rpSBML.rpSBML(fileName)
    rpsbml.readSBML(sbml_path)
    input_rpsbml = rpSBML.rpSBML(fileName+'_merged')
    input_rpsbml.readSBML(inModel)
    rpsbml.mergeModels(input_rpsbml)
    input_rpsbml.writeSBML(tmpOutputFolder)


##
#
#
def runMerge_hdd(inputTar, inModel, outputTar):
    if not os.path.exists(os.getcwd()+'/tmp'):
        os.mkdir(os.getcwd()+'/tmp')
    tmpInputFolder = os.getcwd()+'/tmp/'+''.join(random.choice(string.ascii_lowercase) for i in range(15))
    tmpOutputFolder = os.getcwd()+'/tmp/'+''.join(random.choice(string.ascii_lowercase) for i in range(15))
    os.mkdir(tmpInputFolder)
    os.mkdir(tmpOutputFolder)
    tar = tarfile.open(inputTar, 'r:xz')
    tar.extractall(path=tmpInputFolder)
    tar.close()
    for sbml_path in glob.glob(tmpInputFolder+'/*'):
        fileName = sbml_path.split('/')[-1].replace('.sbml', '')
        singleFBA_hdd(fileName, sbml_path, inModel, tmpOutputFolder, dontMerge, pathway_id)
    with tarfile.open(outputTar, mode='w:xz') as ot:
        for sbml_path in glob.glob(tmpOutputFolder+'/*'):
            fileName = str(sbml_path.split('/')[-1].replace('.sbml', ''))
            info = tarfile.TarInfo(fileName)
            info.size = os.path.getsize(sbml_path)
            ot.addfile(tarinfo=info, fileobj=open(sbml_path, 'rb'))
    shutil.rmtree(tmpInputFolder)
    shutil.rmtree(tmpOutputFolder)


if __name__ == "__main__":
    parser = argparse.ArgumentParser('Given a collection of sbml files as a tar.xz and a SBML files, merge the two and output the results in a tar.xz')
    parser.add_argument('-inModel', type=str)
    parser.add_argument('-inputTar', type=str)
    parser.add_argument('-outputTar', type=str)
    params = parser.parse_args()
    #TODO: detect the changes what how many models are inside the TAR and based on the number determine
    # if you use the _mem or _hdd functions
    #runMerge_mem(params.inputTar, params.inModel, params.outputTar)
    runMerge_hdd(params.inputTar, params.inModel, params.outputTar)
    exit(0)
