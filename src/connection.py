#!/usr/bin/env python

import psycopg2

def get_connection_and_cursor(host, port, database, user, password):
    db_conn = psycopg2.connect(host=host, port=port, database=database,
                              user=user, password=password)

    cursor = db_conn.cursor()
    cursor.execute("SET search_path TO public")

    cursor.execute("""
    create table if not exists intents
    (
        id     serial
            constraint intents_pk
                primary key,
        intent varchar
    );

    alter table intents
        owner to postgres;

    create table if not exists tasks
    (
        id   serial
            constraint tasks_pk
                primary key,
        name varchar
    );

    alter table tasks
        owner to postgres;

    create table if not exists scenarios
    (
        id       serial
            constraint scenarios_pk
                primary key,
        intent   integer
            constraint intents_tasks_intents_null_fk
                references intents,
        task     integer
            constraint intents_tasks_tasks_null_fk
                references tasks,
        priority integer
    );

    alter table scenarios
        owner to postgres;

    create table if not exists scenario_params
    (
        id       serial
            constraint scenario_params_pk
                primary key,
        scenario integer not null
            constraint scenario_params_intents_tasks_null_fk
                references scenarios,
        param    varchar,
        dialogflow_param boolean not null
    );

    alter table scenario_params
        owner to postgres;

    create table if not exists scenario_inputs
    (
        id       serial
            constraint scenario_inputs_pk
                primary key,
        scenario integer
            constraint scenario_inputs_intents_tasks_null_fk
                references scenarios,
        intent   integer
            constraint scenario_inputs_intents_null_fk
                references intents,
        alias    varchar not null
    );

    alter table scenario_inputs
        owner to postgres;
    """)

    db_conn.commit()

    return db_conn, cursor
