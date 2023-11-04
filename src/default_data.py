default_intents = [
        ('intent_call', None),
        ('default', None),
        ('test_bring_goods', None),
        ('test_move_to', None),
        ('test_stop', None),
        ('test_wander', None),
        ('stop', None),
        ('confirm', 'user confirms something, e.g. confirms passing something to robot or taking something from robot. means that user already did what was expected from them so robot can continue its job'),
        ('go to', None),
        ('guide human', None),
        ('patrol', None),
        ('bring jar', None),
        ('bring item', None),
        ('human fell', None),
        ('User recieved', 'user means that he picked up the item from the robot'),
        ('what are you carrying', 'user asks robot what its carrying'),
        ('turn around', 'user asks robot to turn around'),
        ('what are you doing', 'user asks robot what its doing'),
        ('User gave', 'user means that he gave the requested item to the robot'),
    ]
i
default_tasks = [
        ('call', None, None),
        ('idle_tasker', None, None),
        ('bring_goods_new_tasker', 'bring goods', 'going to keeper to ask for goods that master requested. after recieving the goods return back to master with goods.'),
        ('stop', 'stop', None),
        ('bring_jar_tasker', 'bring jar', None),
        ('wander', 'wander', None),
        ('move_to_tasker', 'move to', None),
        ('stop', 'stop', None),
        ('guide_human_tasker', 'guide human', None),
        ('human_fell_tasker', 'human fell', None)
    ]

default_scenarios = [
        ('guide human', 'guide_human_tasker', 5, ['guide_destination', 'human_name'], []),
        ('human fell', 'human_fell_tasker', 9, ['human_name'], []),
        ('bring jar', 'bring_jar_tasker', 5, ['end_pose', 'object_container', 'bring_destination'], []),
        ('go to', 'move_to_tasker', 5, ['place'], []),
        ('stop', 'stop', 10, [], []),
        ('patrol', 'wander', 5, [], []),
        ('intent_call', 'call', 1, ['place'], []),
        ('bring item', 'bring_goods_new_tasker', 5, ['item'], ['confirm', 'User recieved', 'User gave', 'what are you carrying', 'turn around', 'what are you doing']),
        ('default', 'idle_tasker', -999, [], [])
    ]

def insert_default_data(cursor, db_conn):

    cursor.execute("""
        select count(*) from intents
    """)
    intents_count_tuple = cursor.fetchone()
    intents_count = intents_count_tuple[0]
    is_no_intents = intents_count == 0

    if is_no_intents:
        for name, description in default_intents:
            cursor.execute('select nextval(\'intents_id_seq\')')
            intent_id_tuple = cursor.fetchone()
            intent_id = intent_id_tuple[0]

            if description is not None:
                cursor.execute("""
                    insert into intents (id, name, description)
                    values (%s, \'%s\', \'%s\')
                """ % (intent_id, name, description))
            else:
                cursor.execute("""
                    insert into intents (id, name)
                    values (%s, \'%s\')
                """ % (intent_id, name))

    cursor.execute("""
        select count(*) from tasks
    """)
    tasks_count_tuple = cursor.fetchone()
    tasks_count = tasks_count_tuple[0]
    is_no_tasks = tasks_count == 0

    if is_no_tasks:
        for name, display_name, description in default_tasks:
            cursor.execute('select nextval(\'tasks_id_seq\')')
            task_id_tuple = cursor.fetchone()
            task_id = task_id_tuple[0]

            if display_name is not None and description is not None:
                cursor.execute("""
                    insert into tasks (id, name, display_name, description)
                    values (%s, \'%s\', \'%s\', \'%s\')
                """ % (task_id, name, display_name, description))
            elif display_name is not None:
                cursor.execute("""
                    insert into tasks (id, name, display_name)
                    values (%s, \'%s\', \'%s\')
                """ % (task_id, name, display_name))
            elif description is not None:
                cursor.execute("""
                    insert into tasks (id, name, description)
                    values (%s, \'%s\', \'%s\')
                """ % (task_id, name, description))
            else:
                cursor.execute("""
                    insert into tasks (id, name)
                    values (%s, \'%s\')
                """ % (task_id, name))

    cursor.execute("""
        select count(*) from scenarios
    """)
    scenarios_count_tuple = cursor.fetchone()
    scenarios_count = scenarios_count_tuple[0]
    is_no_scenarios = scenarios_count == 0

    if is_no_scenarios:
        for intent_name, task_name, priority, params, inputs in default_scenarios:
            cursor.execute("""
                select intents.id from intents where intents.name = \'%s\'
            """ % intent_name)
            intent_id_tuple = cursor.fetchone()
            intent_id = intent_id_tuple[0]

            cursor.execute("""
                select tasks.id from tasks where tasks.name = \'%s\'
            """ % task_name)
            task_id_tuple = cursor.fetchone()
            task_id = task_id_tuple[0]

            cursor.execute('select nextval(\'scenarios_id_seq\')')

            scenario_id_tuple = cursor.fetchone()

            scenario_id = scenario_id_tuple[0]

            cursor.execute("""
                insert into scenarios (id, intent, task, priority)
                values (%s, %s, %s, %s)
            """ % (scenario_id, intent_id, task_id, priority))

            cursor.execute("""
                select count(*) from scenario_params where scenario_params.scenario = %s
            """ % scenario_id)
            params_count_tuple = cursor.fetchone()
            params_count = params_count_tuple[0]
            is_no_params = params_count == 0

            if is_no_params:
                for param in params:
                    cursor.execute('select nextval(\'scenario_params_id_seq\')')
                    param_id_tuple = cursor.fetchone()
                    param_id = param_id_tuple[0]

                    cursor.execute("""
                        insert into scenario_params (id, scenario, param)
                        values (%s, %s, \'%s\')
                    """ % (param_id, scenario_id, param))

            cursor.execute("""
                select count(*) from scenario_inputs where scenario_inputs.scenario = %s
            """ % scenario_id)
            inputs_count_tuple = cursor.fetchone()
            inputs_count = inputs_count_tuple[0]
            is_no_inputs = inputs_count == 0

            if is_no_inputs:
                for input_name in inputs:
                    cursor.execute('select nextval(\'scenario_inputs_id_seq\')')
                    input_id_tuple = cursor.fetchone()
                    input_id = input_id_tuple[0]

                    cursor.execute("""
                        select intents.id from intents where intents.name = \'%s\'
                    """ % input_name)

                    input_intent_id_tuple = cursor.fetchone()

                    input_intent_id = input_intent_id_tuple[0]

                    cursor.execute("""
                        insert into scenario_inputs (id, scenario, intent)
                        values (%s, %s, %s)
                    """ % (input_id, scenario_id, input_intent_id))

    db_conn.commit()
