FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# WORKDIR /app
WORKDIR /code

#COPY requirements.txt requirements.txt
# COPY ./requirements.txt /app/
COPY ./requirements.txt /code/

RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt

#COPY . .
# COPY . /app
COPY . /code

# Now, tell Docker what command to run when the image is executed inside a container using the CMD command. Note that you need to make the application externally visible (i.e. from outside the container) by specifying --host=0.0.0.0.
#CMD ["python3", "-m" , "flask", "run", "--host=0.0.0.0"]
#ENV PORT=8000
#CMD gunicorn oc_lettings_site.wsgi --bind 0.0.0.0:$PORT
#CMD ["python3", "manage.py" , "runserver", "--host=0.0.0.0"]
#CMD ["python", "manage.py" , "runserver", "0.0.0.0:8000"]
