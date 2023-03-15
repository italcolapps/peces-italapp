FROM python:3.7

RUN mkdir wd
WORKDIR wd

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

COPY . ./

CMD ["python", "app.py"]
