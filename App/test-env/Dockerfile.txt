FROM python:3.8.10

RUN mkdir /app

WORKDIR /app
COPY . .

RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["python"]
CMD ["application.py"]
