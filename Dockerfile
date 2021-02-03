FROM python:3.8-slim
RUN apt-get update && apt-get -y install cron
RUN pip3 install virtualenv pipenv

RUN useradd -ms /bin/bash stonks
USER stonks
WORKDIR /home/stonks

ENV VIRTUAL_ENV=/home/stonks/venv
RUN virtualenv -p python3 $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY Pipfile* ./
RUN pipenv lock --keep-outdated --requirements > requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_md
RUN python -m spacy download nl_core_news_sm

# Create directory structure and copy dagster pipelines
RUN mkdir -p dagster/home dagster/app dagster/var/storage dagster/var/db
COPY . /home/stonks/dagster/app/

# Copy dagster instance YAML to dagster home dir
COPY dagster.yaml /home/stonks/dagster/home/
WORKDIR /home/stonks/dagster/app/
ENV DAGSTER_HOME=/home/stonks/dagster/home/

EXPOSE 3000

# ENTRYPOINT ["wrapper.sh"]
CMD ./wrapper.sh