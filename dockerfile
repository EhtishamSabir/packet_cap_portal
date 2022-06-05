FROM mongo:latest
# install Python 3
RUN apt-get update && apt-get install -y python3 python3-pip
RUN apt-get -y install python3
RUN apt-get -y install tshark
RUN pip3 install pyshark
RUN pip3 install pymongo flask dnspython
RUN apt-get -y install tshark
ENTRYPOINT [ "python" ]
CMD ["/var/www/html/main.py" ]
EXPOSE 27017 80