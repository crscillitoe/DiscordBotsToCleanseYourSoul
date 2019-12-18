FROM python:3
ADD bot.py /
ADD secrets/client_login_info.json /

ADD requirements.txt /

RUN pip install -r requirements.txt

ENTRYPOINT [ "python3", "bot.py" ]