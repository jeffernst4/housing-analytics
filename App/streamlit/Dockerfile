FROM python:3.8.10

RUN mkdir /app

WORKDIR /app
COPY . .

RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

CMD ["sh", "-c", "streamlit run --browser.serverAddress 0.0.0.0 --server.enableCORS False --server.port 80 --server.enableXsrfProtection False /app/main.py"]

