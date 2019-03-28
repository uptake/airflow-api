#!/usr/bin/env bash
set -e

# Slugify user text is necessary for apache-airflow
export SLUGIFY_USES_TEXT_UNIDECODE=yes

pip install --user ".[test]"

pytest tests
