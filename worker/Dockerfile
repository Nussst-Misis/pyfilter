FROM python:3.9

RUN apt update
RUN apt install -y cmake ffmpeg libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0
RUN pip install poetry
RUN pip install -v --install-option="--no" --install-option="DLIB_USE_CUDA" dlib

ADD ./requirements.txt /worker/

WORKDIR /worker/

RUN pip install -r requirements.txt

ADD ./service /worker/service/

CMD ["python", "-m", "service"]
