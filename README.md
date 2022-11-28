dbt_basic
========
Description: Runs dbt commands (seed, run, test) via bash commands for the jaffle_shop example project

Requirements:
- The dbt project included in this repo under include/dbt
- Local: Make sure you have set SNOWFLAKE_PASSWORD in your .env file
- Cloud: Make sure you create a secret env var for SNOWFLAKE_PASSWORD


Libraries Used:
- dbt-snowflake==1.3.0
- pendulum==2.1.2

dbt_advanced
========
Description: Runs the same commands as dbt_basic above, but parses the steps into individual tasks for finer grain monitoring

Requirements:
- The dbt project included in this repo under include/dbt
- include/dbt_dag_parser.py
- Local: Make sure you have set SNOWFLAKE_PASSWORD in your .env file
- Cloud: Make sure you create a secret env var for SNOWFLAKE_PASSWORD


Libraries Used:
- dbt-snowflake==1.3.0
- pendulum==2.1.2

s3_fivetran_dbt_dag.py
========
Description: Similar to dbt_advanced above; however, utilizes fivetran operators and sensors to sync data from an s3 bucket to snowflake instead of using the dbt seed command

Requirements:
- A Fivetran account (they allow for 14 day free trials) with jobs for the three .csv syncs required for the jaffle_shop project (customers,orders,payments)
- The dbt project included in this repo under include/dbt
- include/dbt_dag_parser.py
- Local: Make sure you have set SNOWFLAKE_PASSWORD in your .env file
- Cloud: Make sure you create a secret env var for SNOWFLAKE_PASSWORD


Libraries Used:
- dbt-snowflake==1.3.0
- pendulum==2.1.2
- airflow-provider-fivetran==1.1.2

