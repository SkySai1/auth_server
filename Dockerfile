FROM python:3.8-slim
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
RUN mkdir data
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
