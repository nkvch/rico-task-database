#!/usr/bin/env python
# encoding: utf8

import rospy
import actionlib
from std_msgs.msg import String, Bool
import tiago_msgs.msg
from task_database.msg import Scenario, TaskSpec, ScenarioInput
from task_database.srv import GetScenarioForIntent, GetScenarioForIntentResponse, GetTaskSpecForIntent, GetTaskSpecForIntentResponse, GetAllTaskNames, GetAllTaskNamesResponse, GetParamsForScenario, GetParamsForScenarioResponse, GetScenarioInputs, GetScenarioInputsResponse, CloneScenarioWithNewIntent, CloneScenarioWithNewIntentResponse, AddParamsForScenario, AddParamsForScenarioResponse
from connection import get_connection_and_cursor
from default_data import insert_default_data
from scenarios_interface import ScenariosInterface
from conversation_msgs.msg import ScenarioIntentWithParams
from conversation_msgs.srv import GetScenariosIntentsWithParams, GetScenariosIntentsWithParamsResponse
from task_database.srv import GetTaskDescription, GetTaskDescriptionResponse


def get_scenario_for_intent(si):
    return lambda req: GetScenarioForIntentResponse(Scenario(*(si.get_scenario_for_intent(req.intent))))


def get_task_spec_for_intent(si):
    return lambda req: GetTaskSpecForIntentResponse(TaskSpec(*(si.get_task_spec_for_intent(req.intent))))


def get_all_tasks_names(si):
    return lambda req: GetAllTaskNamesResponse(si.get_all_tasks_names())


def get_params_for_scenario(si):
    return lambda req: GetParamsForScenarioResponse(si.get_params_for_scenario(req.scenario_id, req.only_dialogflow_params))


def get_scenario_inputs(si):
    return lambda req: GetScenarioInputsResponse(list(map(lambda tupl: ScenarioInput(tupl[0], tupl[1]), si.get_scenario_inputs(req.scenario_id))))


def main():
    rospy.init_node('database', anonymous=True)

    host = rospy.get_param('~host')
    port = rospy.get_param('~port')
    database = rospy.get_param('~database')
    user = rospy.get_param('~user')
    password = rospy.get_param('~password')

    db_conn, cursor = get_connection_and_cursor(
        host, port, database, user, password)
    
    insert_default_data(cursor, db_conn)

    scenarios_interface = ScenariosInterface(db_conn=db_conn, cursor=cursor)

    def clone_scenario_with_new_intent(req):
        print req.exist_scenario_id, type(req.exist_scenario_id), req.new_intent, type(req.new_intent), req.additional_params
        newid = scenarios_interface.clone_scenario_with_new_intent(
            req.exist_scenario_id, req.new_intent, req.additional_params)
        print 'newid', newid
        return CloneScenarioWithNewIntentResponse(newid)

    def add_params_for_scenario(req):
        scenarios_interface.add_params_for_scenario(
            req.scenario_id, req.params)
        return AddParamsForScenarioResponse()

    def get_scenarios_intents_with_params(req):
        print 'get_scenarios_intents_with_params'
        scenarios_intents_with_params = {}
        for scenario_id, intent_name, param_name in scenarios_interface.get_scenarios_intents_with_params():
            print 'scenario_id, intent, param_name', scenario_id, intent_name, param_name
            if scenario_id not in scenarios_intents_with_params:
                scenarios_intents_with_params[scenario_id] = {
                    'scenario_id': scenario_id,
                    'intent_name': intent_name,
                    'params': [param_name] if param_name else []
                }
            elif param_name:
                scenarios_intents_with_params[scenario_id]['params'].append(
                    param_name)
        return GetScenariosIntentsWithParamsResponse(list(
            map(lambda siwp: ScenarioIntentWithParams(
                siwp['scenario_id'], siwp['intent_name'], siwp['params']), scenarios_intents_with_params.values())
        ))
    
    def get_task_description(req):
        (display_name, description) = scenarios_interface.get_task_description(req.task_name)
        return GetTaskDescriptionResponse(display_name, description)

    rospy.Service(
        'get_scenario_for_intent', GetScenarioForIntent, get_scenario_for_intent(scenarios_interface))

    rospy.Service(
        'get_task_spec_for_intent', GetTaskSpecForIntent, get_task_spec_for_intent(scenarios_interface))

    rospy.Service(
        'get_all_tasks_names', GetAllTaskNames, get_all_tasks_names(scenarios_interface))

    rospy.Service(
        'get_params_for_scenario', GetParamsForScenario, get_params_for_scenario(scenarios_interface))

    rospy.Service(
        'get_scenario_inputs', GetScenarioInputs, get_scenario_inputs(scenarios_interface))

    rospy.Service(
        'clone_scenario_with_new_intent', CloneScenarioWithNewIntent, clone_scenario_with_new_intent)

    rospy.Service(
        'add_params_for_scenario', AddParamsForScenario, add_params_for_scenario)

    rospy.Service(
        'get_scenarios_intents_with_params', GetScenariosIntentsWithParams, get_scenarios_intents_with_params)
    
    rospy.Service(
        'get_task_description', GetTaskDescription, get_task_description)


    rospy.spin()


if __name__ == '__main__':
    main()
