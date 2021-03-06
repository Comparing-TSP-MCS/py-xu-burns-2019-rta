import multiprocessing

# Set number of parallel jobs
# Watchout: in dual-core version PARALLEL_JOBS must set to 1.
PARALLEL_JOBS = 1 # multiprocessing.cpu_count()

# Enable/disable models to check
CHECK_NO_MIGRATION = True
CHECK_SEMI_1_BF    = True
CHECK_SEMI_1_FF    = True
CHECK_SEMI_1_WF    = True
CHECK_SEMI_2_WF    = True
CHECK_SEMI_2_FF    = True
CHECK_SEMI_2_BF    = True

NUMBER_OF_APPROACHES = 7

# Enable/disable tests to run
RUN_FIRST_TEST = True
RUN_SECOND_TEST = False
RUN_THIRD_TEST = False
RUN_FOURTH_TEST = False

# Select bin-packing algorithm to use
FIRST_FIT_BP = False
BEST_FIT_BP  = True 
WORST_FIT_BP = False

# Select version of Vestal's algorithm to use
VESTAL_CLASSIC = False
VESTAL_WITH_MONITOR = False
# Always consider HI-crit interference from HI-crit tasks
ALWAYS_HI_CRIT = True

# Number of tests to run for each Utilization step
NUMBER_OF_TESTS = 2

# Results will be saved in RESULTS_DIR
RESULTS_DIR = './results_dualcore_2/'

# The following list contains the order in which the cores enter HI-crit mode
# All the possible combinations are tested (in Model 3 a single core entering
# HI-crit mode will interfere with all the others)
CORES_MODE_CHANGES = [
  ['c1'],
  ['c2']
]

# This is the configuration used to test the NO MIGRATION model
CORES_NO_MIGRATION = {
  'c1': {'tasks': [], 'considered': False, 'utilization': 0},
  'c2': {'tasks': [], 'considered': False, 'utilization': 0}
}

# This is the configuration used to test MODEL 1
CORES_MODEL_1 = {
  'c1': {
    # List of tasks scheduled on this core
    'tasks': [],
    # Flag to determine if the core was already considered for a particular
    # task scheduling
    'considered': False,
    # Total utilization
    'utilization': 0,
    # Flag to indicate criticality change
    'crit': False,
    # Migration routes
    'migration': [
      ['c2']
    ]
  },
  'c2': {
    'tasks': [],
    'considered': False,
    'utilization': 0,
    'crit': False,
    'migration': [
      ['c1']
    ]
  }
}

ID_CURRENT_SYSTEM = 0

SYSTEM_MODEL = {
  'id': ID_CURRENT_SYSTEM,

  'c1': {
    # List of tasks scheduled on this core
    'tasks': [],
    # Flag to determine if the core was already considered for a particular
    # task scheduling
    'considered': False,
    # Total utilization
    'utilization': 0,
    # Flag to indicate criticality change
    'crit': False,
    # Migration routes
    'migration': [
      ['c2']
    ]
  },

  'c2': {
    'tasks': [],
    'considered': False,
    'utilization': 0,
    'crit': False,
    'migration': [
      ['c1']
    ]
  }

}

SYSTEMS_SCHEDULABLE_SEMI1BF = []

last_time_on_core_i = {'c1': [], 'c2': []}
last_time_on_core_i_with_additional_migrating_task = {'c1': [], 'c2': []}
where_last_mod_mig = ""

XML_Files = {
  1: {
    'semi1FF': './XML_tasksets/experiment_1/semi1-FF.xml',
    'semi1BF': './XML_tasksets/experiment_1/semi1-BF.xml',
    'semi1WF': './XML_tasksets/experiment_1/semi1-WF.xml',
    'semi2FF': './XML_tasksets/experiment_1/semi2-FF.xml',
    'semi2BF': './XML_tasksets/experiment_1/semi2-BF.xml',
    'semi2WF': './XML_tasksets/experiment_1/semi2-WF.xml'
  },

  2: {
    'semi1FF': './XML_tasksets/experiment_2/semi1-FF.xml',
    'semi1BF': './XML_tasksets/experiment_2/semi1-BF.xml',
    'semi1WF': './XML_tasksets/experiment_2/semi1-WF.xml',
    'semi2FF': './XML_tasksets/experiment_2/semi2-FF.xml',
    'semi2BF': './XML_tasksets/experiment_2/semi2-BF.xml',
    'semi2WF': './XML_tasksets/experiment_2/semi2-WF.xml'
  },
  
  3: {
    'semi1FF': './XML_tasksets/experiment_3/semi1-FF.xml',
    'semi1BF': './XML_tasksets/experiment_3/semi1-BF.xml',
    'semi1WF': './XML_tasksets/experiment_3/semi1-WF.xml',
    'semi2FF': './XML_tasksets/experiment_3/semi2-FF.xml',
    'semi2BF': './XML_tasksets/experiment_3/semi2-BF.xml',
    'semi2WF': './XML_tasksets/experiment_3/semi2-WF.xml'
  },

  4: {
    'semi1FF': './XML_tasksets/experiment_4/semi1-FF.xml',
    'semi1BF': './XML_tasksets/experiment_4/semi1-BF.xml',
    'semi1WF': './XML_tasksets/experiment_4/semi1-WF.xml',
    'semi2FF': './XML_tasksets/experiment_4/semi2-FF.xml',
    'semi2BF': './XML_tasksets/experiment_4/semi2-BF.xml',
    'semi2WF': './XML_tasksets/experiment_4/semi2-WF.xml'
  },
}

Ada_Paths = {
  1: {
    'semi1FF': './Ada_tasksets/experiment_1/semi1-FF/',
    'semi1BF': './Ada_tasksets/experiment_1/semi1-BF/',
    'semi1WF': './Ada_tasksets/experiment_1/semi1-WF/',
    'semi2FF': './Ada_tasksets/experiment_1/semi2-FF/',
    'semi2BF': './Ada_tasksets/experiment_1/semi2-BF/',
    'semi2WF': './Ada_tasksets/experiment_1/semi2-WF/'
  },

  2: {
    'semi1FF': './Ada_tasksets/experiment_2/semi1-FF/',
    'semi1BF': './Ada_tasksets/experiment_2/semi1-BF/',
    'semi1WF': './Ada_tasksets/experiment_2/semi1-WF/',
    'semi2FF': './Ada_tasksets/experiment_2/semi2-FF/',
    'semi2BF': './Ada_tasksets/experiment_2/semi2-BF/',
    'semi2WF': './Ada_tasksets/experiment_2/semi2-WF/'
  },
  
  3: {
    'semi1FF': './Ada_tasksets/experiment_3/semi1-FF/',
    'semi1BF': './Ada_tasksets/experiment_3/semi1-BF/',
    'semi1WF': './Ada_tasksets/experiment_3/semi1-WF/',
    'semi2FF': './Ada_tasksets/experiment_3/semi2-FF/',
    'semi2BF': './Ada_tasksets/experiment_3/semi2-BF/',
    'semi2WF': './Ada_tasksets/experiment_3/semi2-WF/'
  },

  4: {
    'semi1FF': './Ada_tasksets/experiment_4/semi1-FF/',
    'semi1BF': './Ada_tasksets/experiment_4/semi1-BF/',
    'semi1WF': './Ada_tasksets/experiment_4/semi1-WF/',
    'semi2FF': './Ada_tasksets/experiment_4/semi2-FF/',
    'semi2BF': './Ada_tasksets/experiment_4/semi2-BF/',
    'semi2WF': './Ada_tasksets/experiment_4/semi2-WF/'
  },
}

GLOBAL_TASKSET_ID = 0

RUNTIME_DIR = '""'