# endcoding: utf8

from scenarios_interface import ScenariosInterface
from connection import get_connection_and_cursor
# import rospy
# from task_database.srv import GetScenarioForIntent, GetTaskSpecForIntent, GetAllTaskNames, CloneScenarioWithNewIntent
import subprocess
import os
import json

# db_conn, cursor = get_connection_and_cursor("localhost", "5432", "rico", "postgres", "postgres")

# si = ScenariosInterface(db_conn, cursor)

# print si.get_params_for_scenario(24, True)

python3_path = os.path.abspath('../../task_database/src/python3_script/venv/bin/python')
script_path = os.path.abspath('../../task_database/src/python3_script/script.py')


data = subprocess.check_output([
    python3_path,
    script_path,
    "podaj mi proszę gumkę zieloną",
  ])

# dict_data = json.loads(data)

print data
