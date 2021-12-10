# python version
FROM python:3.7

# task working directory
WORKDIR /task2.1.3

# installing the requirements
RUN pip install Flask
RUN pip install flask
RUN pip install flask-cors
RUN pip install requests
RUN pip install flask_oidc


# getting the REST api file and secrets file for keycloak to docker image
COPY secrets.json .
COPY app.py .


# running the command to run the application
CMD ["python","app.py"]