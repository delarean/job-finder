FROM apache/airflow:2.10.5

USER root
COPY pyproject.toml README.md /opt/jobsearch/
COPY src /opt/jobsearch/src
RUN chown -R airflow:root /opt/jobsearch

USER airflow
RUN pip install --no-cache-dir -e /opt/jobsearch
