FROM jjanzic/docker-python3-opencv
ADD bot.py /
ADD pixel_processor.py /
ADD image_processor.py /
ADD constants_two.py /
ADD svgs/ svgs/
ADD secrets/client_login_info.json /

ADD requirements.txt /

RUN pip install -r requirements.txt
RUN apt update
RUN apt install -y vim

ENTRYPOINT [ "python3", "bot.py" ]