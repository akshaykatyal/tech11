# python version
FROM python:3.7

# task working directory
WORKDIR /task2.1.1

# installing the requirements
RUN pip install Flask

# getting the REST api file to docker image
COPY api_hello.py .

# running the command
CMD ["python","api_hello.py"]