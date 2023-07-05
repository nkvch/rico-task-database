class ScenariosInterface:
    def __init__(self, db_conn, cursor):
        self.cursor = cursor
        self.db_conn = db_conn

    def create_intent(self, intent_name):
        self.cursor.execute('select nextval(\'intents_id_seq\')')
        intent_id_tuple = self.cursor.fetchone()
        intent_id = intent_id_tuple[0]

        print 'got new id', intent_id

        self.cursor.execute("""
            insert into intents(id, intent) values (%s, '%s')
        """ % (intent_id, intent_name))

        print 'creted new intent', intent_id

        return intent_id
    
    def create_scenario(self, intent_id, task_id, priority):
        self.cursor.execute('select nextval(\'scenarios_id_seq\')')
        scenario_id_tuple = self.cursor.fetchone()
        scenario_id = scenario_id_tuple[0]
        
        self.cursor.execute("""
            insert into scenarios(id, intent, task, priority) values (%s, %s, %s, %s)
        """ % (scenario_id, intent_id, task_id, priority))

        return scenario_id
    
    def get_scenarios_with_full_data(self): 
        self.cursor.execute("""
            select scenarios.id, i.name, t.name, priority
            from scenarios
            join intents i on scenarios.intent = i.id
            join tasks t on scenarios.task = t.id
        """)

        data = self.cursor.fetchall()

        return data

    def get_all_tasks_names(self):
        self.cursor.execute("""
            select name from tasks
        """)

        data = self.cursor.fetchall()

        return list(map(lambda tup: tup[0], data))

    def add_params_for_scenario(self, scenario_id, params):
        params_insert_statement = '\n'.join(list(map(
            lambda param: "insert into scenario_params(id, scenario, param) values (default, %s, \'%s\');" % (scenario_id, param),
            params,
        )))

        self.cursor.execute(params_insert_statement)
        self.save_changes()
    
    def add_inputs_for_scenario(self, scenario_id, inputs):
        inputs_insert_statement = '\n'.join(list(map(
            lambda input_tuple: """
                insert into scenario_inputs(id, scenario, intent, alias)
                values (
                    default,
                    %s,
                    %s,
                    \'%s\'
                );
            """ % (scenario_id, input_tuple[0], input_tuple[1]),
            inputs,
        )))

        self.cursor.execute(inputs_insert_statement)

    def save_changes(self):
        self.db_conn.commit()

    def get_scenario_for_intent(self, intent_name):
        self.cursor.execute("""
            select scenarios.id, scenarios.intent, scenarios.task, scenarios.priority
            from scenarios join intents i on scenarios.intent = i.id where i.name = \'%s\'
        """ % intent_name)

        data = self.cursor.fetchone()

        return data

    def get_task_spec_for_intent(self, intent_name):
        self.cursor.execute("""
            select scenarios.id, i.name, t.name, priority from scenarios
            join intents i on scenarios.intent = i.id
            join tasks t on scenarios.task = t.id where i.name = \'%s\'
        """ % intent_name)

        data = self.cursor.fetchone()

        scenario_id, intent, name, priority = data

        params = self.get_params_for_scenario(scenario_id)

        return (intent, name, priority, params)

    def get_scenario_inputs(self, scenario_id):
        self.cursor.execute("""
            select scenario_inputs.alias, i.name, i.description from scenario_inputs
            join intents i on i.id = scenario_inputs.intent
            where scenario_inputs.scenario=%s""" % scenario_id)

        result = self.cursor.fetchall()

        return result


    def add_scenario_with_new_intent(self, intent_name, task_id, priority, params, inputs):
        intent_id = self.create_intent(intent_name)
        scenario_id = self.create_scenario(intent_id, task_id, priority)

        self.add_params_for_scenario(scenario_id, params)
        self.add_inputs_for_scenario(scenario_id, inputs)
        self.save_changes()

        return scenario_id


    def clone_scenario_with_new_intent(self, exist_scenario_id, new_intent, additional_params):
        # intent_name, task_name, priority, params, inputs = self.get_task(existing_intent)
        print 'clone_scenario_with_new_intent', new_intent
        intent_id = self.create_intent(new_intent)

        self.cursor.execute('select nextval(\'scenarios_id_seq\')')
        scenario_id_tup = self.cursor.fetchone()
        scenario_id = scenario_id_tup[0]

        self.cursor.execute("""
            insert into scenarios(id, intent, task, priority) values (
                %s,
                %s, 
                (select task from scenarios where id=%s), 
                (select priority from scenarios where id=%s)
            )
        """ % (scenario_id, intent_id, exist_scenario_id, exist_scenario_id))

        self.cursor.execute('select intent, alias from scenario_inputs where scenario = %s' % exist_scenario_id)
        inputs = self.cursor.fetchall()

        self.add_inputs_for_scenario(scenario_id, inputs)

        self.cursor.execute('select param from scenario_params where scenario = %s' % exist_scenario_id)
        exist_params_tups = self.cursor.fetchall()
        exist_params = list(map(lambda tup: tup[0], exist_params_tups))

        self.add_params_for_scenario(scenario_id, exist_params + additional_params)
        self.save_changes()

        return scenario_id

    def get_params_for_scenario(self, scenario_id, only_dialogflow_params=False):
        query = """
            select sp.param from scenarios
            join scenario_params sp on scenarios.id = sp.scenario
            where scenarios.id=\'%s\'""" % scenario_id

        if only_dialogflow_params:
            query += ' and sp.dialogflow_param = true'

        self.cursor.execute(query)
        params_tuples = self.cursor.fetchall()
        params = list(map(lambda tup: tup[0], params_tuples))

        return params
    
    def get_scenarios_intents_with_params(self):
        # allow null for scenario_params
        self.cursor.execute("""
            select s.id, i.name, sp.param from scenarios s
            join intents i on s.intent = i.id
            left join scenario_params sp on s.id = sp.scenario
            where i.name not like 'test_%' and i.name != 'default' and i.name != 'intent_call'
        """)

        data = self.cursor.fetchall()

        return data
    
    def get_task_description(self, task_name):
        self.cursor.execute("""
            select display_name, description from tasks where name=\'%s\'
        """ % task_name)

        data = self.cursor.fetchone()

        return data
