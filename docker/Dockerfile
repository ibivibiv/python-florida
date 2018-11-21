#Download base image from known working dyomite conductor image
FROM ubuntu:16.04
 
# Update Software repository
RUN apt-get update

#install libraries
RUN apt-get install -y python python-pip wget

#add repos for pip
RUN pip install flask kubernetes



#get florida python
RUN wget https://raw.githubusercontent.com/ibivibiv/python-florida/master/florida.py
RUN wget https://raw.githubusercontent.com/ibivibiv/python-florida/master/config.properties


# get the environment command setup
COPY start.sh /start.sh
CMD ["/start.sh"]

# Default port to acccess Dynomite
RUN echo 'Exposing client port 8080 for Florida'
EXPOSE 8080
