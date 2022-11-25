import os
import logging
logger = logging.getLogger(__name__)

class FixedPointConverter:
  '''
  A Python wrapper around ap_fixed types to easily emulate the correct number representations
  '''

  def __init__(self, type_string):
    '''
    Construct the FixedPointConverter. Compiles the c++ library to use for conversions
    args:
      type_string : string for the ap_ type, e.g. ap_fixed<16,6,AP_RND,AP_SAT>
    '''
    logger.info(f'Constructing converter for {type_string}')
    self.type_string = type_string
    self.sani_type = type_string.replace('<','_').replace('>','').replace(',','_')
    filedir = os.path.dirname(os.path.abspath(__file__))
    cpp_filedir = f"./.fp_converter_{self.sani_type}"
    cpp_filename = cpp_filedir + f'/{self.sani_type}.cpp'
    os.makedirs(cpp_filedir, exist_ok=True)

    fin = open(f'{filedir}/fixed_point_conversions.cpp', 'r')
    fout = open(cpp_filename, 'w')
    for line in fin.readlines():
      newline = line
      if '// conifer insert typedef' in line:
        newline =  f"typedef {type_string} T;\n"
      fout.write(newline)
    fin.close()
    fout.close()

    curr_dir = os.getcwd()
    os.chdir(cpp_filedir)
    cmd = f"g++ -O3 -shared -std=c++11 -fPIC $(python3 -m pybind11 --includes) -I/cvmfs/cms.cern.ch/slc7_amd64_gcc900/external/hls/2019.08/include/ {self.sani_type}.cpp -o {self.sani_type}.so"
    logger.debug(f'Compiling with command {cmd}')
    try:
      ret_val = os.system(cmd)
      if ret_val != 0:
        raise Exception(f'Failed to compile FixedPointConverter {self.sani_type}.cpp')
    finally:
      os.chdir(curr_dir)
    
    os.chdir(cpp_filedir)
    logger.debug(f'Importing compiled module {self.sani_type}.so')
    try:
      import importlib.util
      spec = importlib.util.spec_from_file_location('fixed_point', f'{self.sani_type}.so')
      self.lib = importlib.util.module_from_spec(spec)
      spec.loader.exec_module(self.lib)
    except ImportError:
      os.chdir(curr_dir)
      raise Exception("Can't import pybind11 bridge, is it compiled?")
    os.chdir(curr_dir)

  def to_int(self, x):
    return self.lib.to_int(x)

  def to_double(self, x):
    return self.lib.to_double(x)

  def from_int(self, x):
    return self.lib.from_int(x)