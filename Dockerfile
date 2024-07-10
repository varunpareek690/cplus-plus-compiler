FROM public.ecr.aws/lambda/python:3.8

RUN yum install -y gcc-c++ wget

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . ${LAMBDA_TASK_ROOT}

CMD ["app.lambda_handler"]
