FROM scratch

# This is a placeholder MongoDB container
# Used for testing Docker setup only

VOLUME /data/db
EXPOSE 27017

CMD echo "This is a placeholder MongoDB container"
