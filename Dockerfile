FROM public.ecr.aws/lambda/python:3.13

WORKDIR /var/task

COPY src ./src
COPY pyproject.toml ./pyproject.toml

ENV PYTHONPATH=/var/task/src

CMD ["forward_received_email.lambda_function.lambda_handler"]
