FROM python
ADD gradebook /gradebook
ADD requirements.txt /
RUN pip install -r requirements.txt
WORKDIR /gradebook
CMD python gradebook.py