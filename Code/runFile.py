#runfile for parameter sweeps and suites

from bvm_suite import *
from bvm_sweep import *
import pandas as pd
import numpy as np
import math

suite = bvmSuite({"p":.3, "o":.20, "d":.55,"issues":3, "l_steps":1000, "n_agents":50, 'CI2':True}, 2)
suite.run()

sweep = bvmSweep({"issues":3, "l_steps":1500,'CI2':True, "n_agents":100, "p":0.20, "d":0.55},{"o":np.arange(0.05, 0.45, 0.05)}, 10)
sweep.run()

data = sweep.getData()

print(data)
