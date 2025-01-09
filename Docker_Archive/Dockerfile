FROM python:3.8-buster
COPY requirements_pdu.txt .
COPY setup.sh .
COPY Streamlit_App /app/Streamlit_App
RUN apt-get update && apt-get install -y libx11-dev libeigen3-dev libccd-dev octomap-tools ffmpeg libsm6 libxext6
RUN pip install --upgrade pip
RUN pip3 install -r requirements_pdu.txt
ENV PORT=8085
RUN ./setup.sh
WORKDIR /app
CMD ["streamlit","run","Streamlit_App/Main_v0.21.py"]
EXPOSE 8085
