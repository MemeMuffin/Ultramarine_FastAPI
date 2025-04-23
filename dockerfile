FROM python:3.13.2
WORKDIR /ultramarinesFastAPI
COPY ./requirements.txt /ultramarinesFastAPI/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /ultramarinesFastAPI/requirements.txt
COPY . /ultramarinesFastAPI
CMD ["fastapi", "run", "./main.py", "--port", "800"]