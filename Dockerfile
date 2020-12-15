# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8

# set the working directory in the container
WORKDIR /code

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv /opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
EXPOSE 5000
# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN . /opt/venv/bin/activate && pip install -r requirements.txt && pip install gunicorn

# # Switching to a non-root user, please refer to https://aka.ms/vscode-docker-python-user-rights
# RUN useradd appuser && chown -R appuser /app
# USER appuser
COPY ./tester .

# command to run on container start
CMD ["gunicorn"  , "--bind", "0.0.0.0:5000", "tester:create_app()"]
