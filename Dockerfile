FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
ENV PYTHONPATH="/app:${PYTHONPATH}"
RUN mkdir -p /app/tmp

EXPOSE 8501
ENV PORT 8501

RUN apt-get update -y && apt-get upgrade -y && \
  apt-get install -y libgl1-mesa-dev libglib2.0-0

COPY .streamlit/ .streamlit/

COPY requirements.lock .
RUN sed '/-e/d' requirements.lock > requirements.txt
RUN pip install -r requirements.txt

COPY sample_ai_chat/ sample_ai_chat/

CMD ["python", "scripts/run_start.py"]
