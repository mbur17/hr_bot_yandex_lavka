FROM python:3.11

WORKDIR /src

COPY ./requirements-bot.txt .
RUN pip install --no-cache-dir -r requirements-bot.txt

COPY src/bot ./bot

CMD ["python", "-m", "bot.main"]
