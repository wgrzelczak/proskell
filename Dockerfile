# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8

# set the working directory in the container
WORKDIR /code

EXPOSE 2000
# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt && pip install gunicorn

COPY . .

# command to run on container start
# CMD ["gunicorn"  , "--bind", "0.0.0.0:2000", "runtime_environment:create_app\(\)"]
CMD ["flask"  , "run", "--host", "0.0.0.0"]