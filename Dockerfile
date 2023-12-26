FROM python:3.9

WORKDIR /python-docker

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY NPCCreator/ .

CMD ["python", "app.py"]
