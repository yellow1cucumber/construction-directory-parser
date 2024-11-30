FROM python:3.12-alpine

WORKDIR /backend

RUN apk add --no-cache gcc musl-dev libffi-dev

COPY requirements.txt /backend/requirements.txt
RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r /backend/requirements.txt

COPY . /backend

EXPOSE 5000

CMD ["python3", "main.py"]