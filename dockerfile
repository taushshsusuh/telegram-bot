FROM python:3.9
RUN pip install playwright
RUN playwright install --with-deps chromium
COPY . .
CMD ["python", "main.py"]
