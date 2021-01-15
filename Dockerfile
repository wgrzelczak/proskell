# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8

WORKDIR /var/proskell
# copy the dependencies file to the working directory
COPY requirements.txt requirements.txt

# install dependencies
RUN pip install -r requirements.txt && pip install gunicorn
# set the working directory in the container

COPY . /var/proskell
EXPOSE 4000

COPY . .

# command to run on container start
# CMD ["gunicorn"  , "--bind", "0.0.0.0:4000", "runtime_environment.wsgi:app"]
# CMD ["flask"  , "run", "--host", "0.0.0.0"]
CMD ["gunicorn", "--reload", "--bind", "0.0.0.0:4000", "runtime_environment.wsgi:app"]