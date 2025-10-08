FROM python:3.10-slim
RUN pip install --no-cache-dir kubernetes
COPY controller/dynamic_label_controller.py /controller/dynamic_label_controller.py
WORKDIR /controller
CMD ["python", "dynamic_label_controller.py"]
