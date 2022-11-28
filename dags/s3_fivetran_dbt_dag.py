from airflow import DAG
import json

from fivetran_provider.operators.fivetran import FivetranOperator
from fivetran_provider.sensors.fivetran import FivetranSensor
from airflow.operators.bash import BashOperator


from airflow.models.baseoperator import chain

from datetime import datetime, timedelta

DBT_PROJECT_DIR = "/usr/local/airflow/dbt"


default_args = {
    "owner": "Airflow",
    "start_date": datetime(2021, 4, 6),
}

dag = DAG(
    dag_id="s3_fivetran_dbt_dag",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
)

with dag:
    fivetran_customers_start = FivetranOperator(
        task_id="fivetran_customers_start",
        fivetran_conn_id="fivetran_default",
        connector_id="someone_continuity",
    )

    fivetran_customers_wait = FivetranSensor(
        task_id="fivetran_customers_wait",
        fivetran_conn_id="fivetran_default",
        connector_id="someone_continuity",
        poke_interval=5,
    )

    fivetran_orders_start = FivetranOperator(
        task_id="fivetran_orders_start",
        fivetran_conn_id="fivetran_default",
        connector_id="subjugation_snide",
    )

    fivetran_orders_wait = FivetranSensor(
        task_id="fivetran_orders_wait",
        fivetran_conn_id="fivetran_default",
        connector_id="subjugation_snide",
        poke_interval=5,
    )

    fivetran_payments_start = FivetranOperator(
        task_id="fivetran_payments_start",
        fivetran_conn_id="fivetran_default",
        connector_id="stroked_slab",
    )

    fivetran_payments_wait = FivetranSensor(
        task_id="fivetran_payments_wait",
        fivetran_conn_id="fivetran_default",
        connector_id="stroked_slab",
        poke_interval=5,
    )

    def load_manifest():
        local_filepath = f"{DBT_PROJECT_DIR}/target/manifest.json"
        with open(local_filepath) as f:
            data = json.load(f)
        return data

    def make_dbt_task(node, dbt_verb):
        """Returns an Airflow operator either run and test an individual model"""
        GLOBAL_CLI_FLAGS = "--no-write-json"
        model = node.split(".")[-1]
        if dbt_verb == "run":
            dbt_task = BashOperator(
                task_id=node,
                bash_command=(
                    f"dbt {GLOBAL_CLI_FLAGS} {dbt_verb} --target dev --models {model} "
                    f"--profiles-dir {DBT_PROJECT_DIR} --project-dir {DBT_PROJECT_DIR}"
                )
            )
        elif dbt_verb == "test":
            node_test = node.replace("model", "test")
            dbt_task = BashOperator(
                task_id=node_test,
                bash_command=(
                    f"dbt {GLOBAL_CLI_FLAGS} {dbt_verb} --target dev --models {model} "
                    f"--profiles-dir {DBT_PROJECT_DIR} --project-dir {DBT_PROJECT_DIR}"
                )
            )
        return dbt_task


    data = load_manifest()
    dbt_tasks = {}

    for node in data["nodes"].keys():
        if node.split(".")[0] == "model":
            node_test = node.replace("model", "test")
            dbt_tasks[node] = make_dbt_task(node, "run")
            dbt_tasks[node_test] = make_dbt_task(node, "test")

    for node in data["nodes"].keys():
        if node.split(".")[0] == "model":
            # Set dependency to run tests on a model after model runs finishes
            node_test = node.replace("model", "test")
            dbt_tasks[node] >> dbt_tasks[node_test]
            # Set all model -> model dependencies
            for upstream_node in data["nodes"][node]["depends_on"]["nodes"]:
                upstream_node_type = upstream_node.split(".")[0]
                if upstream_node_type == "model":
                    chain(
                        [fivetran_customers_start,fivetran_orders_start,fivetran_payments_start],
                        [fivetran_customers_wait,fivetran_orders_wait,fivetran_payments_wait],
                        dbt_tasks[upstream_node],
                        dbt_tasks[node]
                    )

    