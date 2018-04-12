FROM python:3.6

RUN apk update && apk upgrade && \ 
    apk add --no-cache git

WORKDIR /home/ec2-user
COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN git clone https://github.com/czhu505/data602-assignment2 /home/ec2-user/apps

EXPOSE 5000
CMD [ "python", "/home/ec2-user/apps/Trader.py" ]