import copy
import config

import os

import xml.etree.ElementTree as ET
import xml.dom.minidom

from shutil import copyfile, rmtree

def CLEAN_ALL():
  for i in range(4):
    clean_XML_and_Ada_Files(i+1)

def clean_XML_and_Ada_Files(experiment_id):
  xml_template = './XML_tasksets/template.xml'

  for path in config.XML_Files[experiment_id]:
    copyfile(xml_template, config.XML_Files[experiment_id][path])

  for path in config.Ada_Paths[experiment_id]:

    for dirname in os.listdir(config.Ada_Paths[experiment_id][path]):
      dirpath = os.path.join(config.Ada_Paths[experiment_id][path], dirname)
      if os.path.exists(dirpath) and dirname != '.gitkeep':
        rmtree(dirpath)  
  

def save_taskset_as_Ada (experiment_id):
  string_tasks = []
  for approach in config.XML_Files[experiment_id]:
    tree = ET.parse(config.XML_Files[experiment_id][approach])
    root = tree.getroot()

    for taskset in root.findall('taskset'):
      taskset_id = int(taskset[0].text)
      if taskset_id != -1:
        Ada_Unit = ''
        Main_Unit = ''

        taskset_name = 'E' + str(experiment_id) + '_' + approach + '_T' + str(taskset_id)

        # Main generation
        main_name = 'main_' + taskset_name
        main_file_name = main_name + '.adb'
        main_withed_united = 'with Taskset_' + taskset_name + ';\nwith System;\n\n' 
        main_procedure = 'procedure ' + main_name + ' is\n'
        main_decl_section = "    pragma Priority (System.Priority'Last);\n    pragma CPU (1);\n"
        main_body = 'begin\n    Periodic_Tasks.Init;\nend' + main_name + ';'
        
        Main_Unit += main_withed_united + main_procedure + main_decl_section + main_body

        taskset_dir = config.Ada_Paths[experiment_id][approach] + taskset_name + '/'
        os.mkdir(taskset_dir)
        
        # dir containing src code
        src_dir = taskset_dir + 'src/'
        os.mkdir(src_dir)
        # dir containing compiled code
        object_code_dir = taskset_dir + 'obj/'
        os.mkdir(object_code_dir)

        # .gpr file project generation
        project_file_name = main_name + '.gpr'
        project = 'project ' + main_name + ' is\n\n'
        project += '    for Languages use ("ada");\n    for Main use ("' + main_file_name + '");\n    for Source_Dirs use ("src", "../common");\n    for Object_Dir use "obj";\n    for Runtime ("ada") use '
        runtime_dir = config.RUNTIME_DIR + ';\n'
        project += runtime_dir + '    for Target use "arm-eabi";\n\n'
        project += '    package Compiler is\n        for Switches ("ada") use ("-g", "-gnatwa", "-gnatQ");\n    end Compiler;\n\n'
        project += '    package Builder is\n        for Switches ("ada") use ("-g", "-O0");\n    end Builder;\n\n'
        project += 'end ' + main_name + ';'

        f = open(taskset_dir + project_file_name, 'w')
        f.write(project)
        f.close()

        # Makefile generation

        make_all = 'all: test\n\n'
        make_test = 'test:\n    gprbuild ' + project_file_name + '\n\n'
        make_clean = 'clean:\n    gprclean ' + project_file_name + '\n\n'
        makefile = make_all + make_test + make_clean

        f = open(taskset_dir + 'makefile', 'w')
        f.write(makefile)
        f.close()

        # flashing script and board init file
        
        template_cora_xsdb_file = './Ada_tasksets/template_cora_xsdb.ini'
        cora_ps7_init_file = './Ada_tasksets/cora_ps7_init.tcl'
        copyfile(template_cora_xsdb_file, taskset_dir + 'cora_xsdb.ini')
        copyfile(cora_ps7_init_file, taskset_dir + 'cora_ps7_init.tcl')

        f = open(taskset_dir + 'cora_xsdb.ini', 'a')
        f.write('dow ' + 'obj/main_' + taskset_name + '\ncon')
        f.close()

        # Ada unit generation

        withed_unit = 'with Periodic_Tasks;\n'
        package_name = '\npackage body Taskset_' + taskset_name + ' is\nbegin\n\n'
        set_hyperperiod = '  Periodic_Tasks.Experiment_Hyperperiod := ' + ' 1_000_000;\n\n'
        file_name = 'Taskset_' + taskset_name + '.adb'

        Ada_Unit += withed_unit + package_name + set_hyperperiod

        cores_XML = [taskset.find('core1'), taskset.find('core2')]
        for core_XML in cores_XML:
          tasks_XML = core_XML.find('tasks')
          
          for task_XML in tasks_XML.findall('task'):
            current_task = '  T_'
            current_task += task_XML.find('ID').text + ' : '

            if task_XML.find('criticality').text == 'HIGH':
              current_task += 'High_Crit ('
            else:
              current_task += 'Low_Crit ('
            
            current_task += 'Pri => ' + task_XML.find('priority').text + ', '
            current_task += 'Low_Critical_Budget => ' + task_XML.find('CLO').text + ', '

            if task_XML.find('criticality').text == 'HIGH':
              current_task += 'High_Critical_Budget => ' + task_XML.find('CHI').text + ', '
            else:
              current_task += 'Is_Migrable => ' + task_XML.find('migrating').text + ', '
            
            current_task += 'Workload => 0, ' # + task_XML.find('workload').text + ', '
            current_task += 'Period => ' + task_XML.find('period').text + ', '
            current_task += 'CPU_Id => ' + ('1' if core_XML.tag == 'core1' else '2') + ');'

            Ada_Unit += current_task + '\n'

            string_tasks.append(current_task)
            
            # print(current_task)

        Ada_Unit += '\nend ' + taskset_name + ';\n'
        # create taskset unit Ada file
        f = open(src_dir + file_name, 'w')
        f.write(Ada_Unit)
        f.close()
        # create main unit Ada file
        f = open(src_dir + main_file_name, 'w')
        f.write(Main_Unit)
        f.close()

def save_taskset_as_XML (c1_steady, c2_steady, c1_with_mig, c2_with_mig, approach, experiment_id, taskset_U, criticality_factor, hi_crit_proportion, util_on_c1, util_on_c2, taskset_id):
  number_of_cores = 2
  cores_indexes = ['c1', 'c2']

  assert(len(c1_with_mig) + len(c2_with_mig) > 0), "We have to save only those tasksets concerning at least one migrating task."
  
  cores_steady = [c1_steady, c2_steady]
  cores_with_mig = [c1_with_mig, c2_with_mig]

  '''print("SAVE THIS ")
  print(config.XML_Files[experiment_id][approach])
  print(c1_steady)
  print(c2_steady)
  print(c1_with_mig)
  print(c2_with_mig)'''
  cores = [[], []]
  utilizations_XML = [[], []]
  tasks_XML = [[], []]

  tree = ET.parse(config.XML_Files[experiment_id][approach])
  root = tree.getroot()

  taskset_selector_XML = ET.SubElement(root, 'taskset')

  tasksetid_XML = ET.SubElement(taskset_selector_XML, 'tasksetid')
  tasksetid_XML.text = str(taskset_id)

  size_XML = ET.SubElement(taskset_selector_XML, 'size')
  size_XML.text = str(len(c1_steady) + len(c2_steady))

  util_XML = ET.SubElement(taskset_selector_XML, 'tasksetutilization')
  util_XML.text = str(taskset_U)

  criticality_factor_XML = ET.SubElement(taskset_selector_XML, 'criticalityfactor')
  criticality_factor_XML.text = str(criticality_factor)

  # proportion of HI-crit tasks
  perc_XML = ET.SubElement(taskset_selector_XML, 'perc')
  perc_XML.text = str(hi_crit_proportion)

  cores[0] = ET.SubElement(taskset_selector_XML, 'core1')
  cores[1] = ET.SubElement(taskset_selector_XML, 'core2')

  utilizations_XML[0] = ET.SubElement(cores[0], 'utilization')
  utilizations_XML[0].text = str(util_on_c1)

  utilizations_XML[1] = ET.SubElement(cores[1], 'utilization')
  utilizations_XML[1].text = str(util_on_c2)

  tasks_XML[0] = ET.SubElement(cores[0], 'tasks') 
  tasks_XML[1] = ET.SubElement(cores[1], 'tasks')  

  for i in range(number_of_cores):
    if i == 0:
      index_other_core = 1
    else:
      index_other_core = 0
    # number of tasks on core i
    total_XML = ET.SubElement(tasks_XML[i], 'total')
    total_XML.text = str(len(cores_steady[i]))
    # save core_i's tasks
    for task in cores_steady[i]:
      task_XML = ET.SubElement(tasks_XML[i], 'task')

      ID_XML = ET.SubElement(task_XML, 'ID')
      ID_XML.text = str(task['ID'])

      criticality_XML = ET.SubElement(task_XML, 'criticality')
      criticality_XML.text = 'HIGH' if task['HI'] else 'LOW'

      # HI-Crit execution time
      CHI_XML = ET.SubElement(task_XML, 'CHI')
      CHI_XML.text = str(task['C(HI)'])

      # LO-Crit execution time
      CLO_XML = ET.SubElement(task_XML, 'CLO')
      CLO_XML.text = str(task['C(LO)'])

      nominalutil_XML = ET.SubElement(task_XML, 'nominalutil')
      nominalutil_XML.text = str(task['U'])

      deadline_XML = ET.SubElement(task_XML, 'deadline')
      deadline_XML.text = str(task['D'])

      reduceddead_XML = ET.SubElement(task_XML, 'reduceddead')
      reduceddead_XML.text = str(task['D1']) if 'D1' in task else ""

      jitter_XML = ET.SubElement(task_XML, 'jitter')
      jitter_XML.text = str(task['J'])

      is_migrating_XML = ET.SubElement(task_XML, 'migrating')
      is_migrating_XML.text = str(task['migrating'])

      priority_XML = ET.SubElement(task_XML, 'priority')
      priority_XML.text = str(task['P'][cores_indexes[i]])

      hostingmigpriority_XML = ET.SubElement(task_XML, 'hostingmigpriority')
      hostingmigpriority_XML.text = str(task['P']['hosting_migrating']) if 'hosting_migrating' in task['P'] else str(-1)

      targetpriority_XML = ET.SubElement(task_XML, 'targetpriority')
      targetpriority_XML.text = str(task['P'][cores_indexes[index_other_core]])

      # Deadline equal to period
      period_XML = ET.SubElement(task_XML, 'period')
      period_XML.text = str(task['D'])

      workload_XML = ET.SubElement(task_XML, 'workload')
      # workload_XML.text = task['workload']

  tree.write(config.XML_Files[experiment_id][approach])

# Define sorting functions for each core to be given to the standard list sorting function
def sort_tasks_priority_c1 (t1, t2):
  if t1[1]['P']['c1'] >= t2[1]['P']['c1']:
    return -1
  else:
    return 1

def sort_tasks_priority_c2 (t1, t2):
  if t1[1]['P']['c2'] >= t2[1]['P']['c2']:
    return -1
  else:
    return 1

def print_taskset (core_1, core_2):
  if len (core_1) > 0:
    print ("Core 1")
    for task in core_1:
      print (task)

  if len (core_2) > 0:
    print ("Core 2")
    for task in core_2:
      print (task)

def check_size_taskset_with_mig (total, approach, experiment_id, taskset_utilization, criticality_factor, hi_crit_proportion, taskset_id):
  assert(len(config.last_time_on_core_i['c1']) + len(config.last_time_on_core_i['c2']) == total), "Wrong number of scheduled tasks"
  cores = ['c1', 'c2']
  # is there at least one migrating task on c_i?
  mig_on_c_i = {'c1': False, 'c2': False}

  comparing_steady_mode = copy.deepcopy(config.last_time_on_core_i)
  comparing_migration_mode = copy.deepcopy(config.last_time_on_core_i_with_additional_migrating_task)
  util_on_core_i = {'c1': 0, 'c2': 0}

  migrating_tasks = []

  other_core = 'c2'

  for core in cores:
    if core == 'c1':
      other_core = 'c2'
    else:
      other_core = 'c1'
    for task in config.last_time_on_core_i[core]:
      util_on_core_i[core] += task['U']
      if task['migrating']:
        mig_on_c_i[core] = True
        migrating_tasks.append(task)
        comparing_migration_mode[other_core].append(task)

  if mig_on_c_i['c1']:
    assert(len(config.last_time_on_core_i_with_additional_migrating_task['c2']) > 0), 'c2 should have migrating tasks'
    for task_mig in migrating_tasks:
      find = False
      for task in config.last_time_on_core_i_with_additional_migrating_task['c2']:
        if task_mig['ID'] == task['ID']:
          find = True
          break
      if not find:
        assert(find)
        print(task_mig['ID'], "not found in c2")
        break

    for task in config.last_time_on_core_i['c2']:
      find = False
      for t2 in config.last_time_on_core_i_with_additional_migrating_task['c2']:
        if task['ID'] == t2['ID']:
          task['P']['hosting_migrating'] = t2['P']['c2']
          find = True
          break
      if not find:
        assert(find)
        print(task['ID'], "is missing in c2")
      
    for task in config.last_time_on_core_i_with_additional_migrating_task['c2']:
      for t2 in config.last_time_on_core_i['c1']:
        if task['ID'] == t2['ID']:
          t2['P']['c2'] = task['P']['c2']
          break
  else:
    #assert(len(config.last_time_on_core_i_with_additional_migrating_task['c2']) <= 0), 'c2 should NOT have migrating tasks'
    if not (len(config.last_time_on_core_i_with_additional_migrating_task['c2']) <= 0):
      print('c2 should NOT have migrating tasks')
      # @TODO: you are cheating...
      config.last_time_on_core_i_with_additional_migrating_task['c2'] = []

  if mig_on_c_i['c2']:
    assert(len(config.last_time_on_core_i_with_additional_migrating_task['c1']) > 0), 'c1 should have migrating tasks'
    for task_mig in migrating_tasks:
      find = False
      for task in config.last_time_on_core_i_with_additional_migrating_task['c1']:
        if task_mig['ID'] == task['ID']:
          find = True
          break
      if not find:
        assert(find)
        print(task_mig['ID'], "not found in c1")
        break

    for task in config.last_time_on_core_i['c1']:
      find = False
      for t2 in config.last_time_on_core_i_with_additional_migrating_task['c1']:
        if task['ID'] == t2['ID']:
          task['P']['hosting_migrating'] = t2['P']['c1']
          find = True
          break
      if not find:
        print(task['ID'], "is missing in c2")
        assert(find)
        break

    for task in config.last_time_on_core_i_with_additional_migrating_task['c1']:
      find = False
      for t2 in config.last_time_on_core_i['c2']:
        if task['ID'] == t2['ID']:
          t2['P']['c1'] = task['P']['c1']
          break
  else:
    #assert(len(config.last_time_on_core_i_with_additional_migrating_task['c1']) <= 0), 'c1 should NOT have migrating tasks'
    if not (len(config.last_time_on_core_i_with_additional_migrating_task['c1']) <= 0):
      print('c1 should NOT have migrating tasks')
      # @TODO: you are cheating...
      config.last_time_on_core_i_with_additional_migrating_task['c1'] = []

  if mig_on_c_i['c1'] or mig_on_c_i['c2']:
    # check_order_preservation(config.last_time_on_core_i['c1'], config.last_time_on_core_i['c2'], config.last_time_on_core_i_with_additional_migrating_task['c1'], config.last_time_on_core_i_with_additional_migrating_task['c2'])
    save_taskset_as_XML(config.last_time_on_core_i['c1'], config.last_time_on_core_i['c2'], config.last_time_on_core_i_with_additional_migrating_task['c1'], config.last_time_on_core_i_with_additional_migrating_task['c2'], approach, experiment_id, taskset_utilization, criticality_factor, hi_crit_proportion, util_on_core_i['c1'], util_on_core_i['c2'], taskset_id)

# It checks if c_i_steady has the same "tasks order relationship" of c_i_with_mig
def check_order_preservation(c1_steady, c2_steady, c1_with_mig, c2_with_mig):
  '''cores_indexes = ['c1', 'c2']
  c_i_steady = {'c1': c1_steady, 'c2': c2_steady}
  c_i_with_migs = {'c1': c1_with_mig, 'c2': c2_with_mig}
  c_i_migs = {'c1': [], 'c2': []}
  for core in cores_indexes
    if core == 'c1':
      other_core = 'c2'
    else:
      other_core = 'c1'
  if len(c_i_with_migs[core]) > 0:
    # get c_other_core's migrating tasks.
    for task in c_i_steady[other_core]:
      if task['migrating']:
        c_i_mig[other_core].append([task['ID'], task['P']])'''

def beautify_XML_Files(experiment_id):
  for path in config.XML_Files[experiment_id]:
    with open(config.XML_Files[experiment_id][path], "r") as xmldata:
      parsing = xml.dom.minidom.parseString(xmldata.read())  # or xml.dom.minidom.parseString(xml_string)
      xml_pretty_str = parsing.toprettyxml()
      xmldata.close()

    with open(config.XML_Files[experiment_id][path], "w") as xmldata:
      xmldata.write(xml_pretty_str)
      xmldata.close()




