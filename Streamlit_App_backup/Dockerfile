FROM python:3-buster
COPY requirements.txt .
COPY setup.sh .
RUN pip3 install -r requirements.txt
ENV PORT=8085
RUN ./setup.sh
WORKDIR /app
CMD ["streamlit","run","Streamlit_App/Main_v0.21.py"]
EXPOSE 8085
