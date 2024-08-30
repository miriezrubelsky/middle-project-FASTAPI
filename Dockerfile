FROM python:3.10-slim-buster

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


RUN pip install --upgrade pip 
    #copy to code directory
COPY . /code    

#set permissions

RUN chmod +x /code/src

RUN pip install --no-cache-dir --upgrade -r code/src/requirements.txt

EXPOSE 8000

WORKDIR /code

ENV PYTHONPATH "${PYTHONPATH}:/code/src"


# Set the entry point for the container
ENTRYPOINT ["python", "main.py"]

# Default command to provide flexibility if no arguments are passed
CMD ["--help"]

# Run the Uvicorn server, specifying the host to be 0.0.0.0 to allow external connections
CMD ["--host", "0.0.0.0", "--port", "8000"]

