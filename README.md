# SES Email Forwarder

Lambda baseada em imagem Docker que recebe e-mails pelo Amazon SES, le o conteudo armazenado no S3, verifica listas de spam e encaminha a mensagem para os enderecos configurados.

## Arquitetura

```text
Amazon SES -> S3 + SNS -> AWS Lambda -> Amazon SES -> destinatarios
```

O Lambda e executado com Python 3.13 e usa Pydantic Settings para carregar a configuracao por variaveis de ambiente. A arquitetura detalhada esta em [docs/architecture.md](docs/architecture.md).

## Requisitos

- Python 3.13
- Poetry
- Docker
- Terraform 1.6 ou superior
- Conta AWS com SES, S3, SNS, Lambda, ECR e IAM habilitados

## Desenvolvimento local

Instale as dependencias:

```bash
poetry install --with dev
```

Execute os testes:

```bash
poetry run pytest
```

Para configurar a aplicacao localmente:

```bash
export AWS_DEFAULT_REGION="us-east-1"
export FORWARD_ADDRESSES="destino1@exemplo.com,destino2@exemplo.com"
export FROM_ADDRESS="AWS Forward <no-reply@%s>"
export LOGGER_LEVEL="INFO"
```

Tambem e possivel usar um arquivo `.env` local.

## Build da imagem

A imagem usa a base oficial `public.ecr.aws/lambda/python:3.13` e o handler `forward_received_email.lambda_function.lambda_handler`.

```bash
docker build -t ses-email-forwarder:local .
```

O Lambda deve usar a imagem publicada no Amazon ECR. O workflow tambem pode publicar uma copia no Docker Hub.

## Infraestrutura

O Terraform cria:

- bucket S3 para os e-mails recebidos;
- topico SNS e assinatura do Lambda;
- receipt rule set e receipt rule do SES;
- repositorio ECR;
- funcao Lambda e grupo de logs;
- roles e policies IAM necessarias.

Crie manualmente o bucket usado pelo backend remoto do Terraform e consulte o exemplo de variaveis:

```bash
cp infra/terraform.tfvars.example infra/terraform.tfvars
cd infra
terraform init \
  -backend-config="bucket=SEU_BUCKET_DE_STATE" \
  -backend-config="key=ses-email-forwarder/terraform.tfstate" \
  -backend-config="region=us-east-1" \
  -backend-config="encrypt=true"
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

O bucket de state e separado do bucket que armazena os e-mails. Mais detalhes estao em [docs/deployment.md](docs/deployment.md).

## GitHub Actions

- `ci.yml`: executa os testes e constroi/publica a imagem.
- `deploy.yml`: dispara com tags no formato `v*`, publica a imagem no ECR e executa o Terraform.

Configure os secrets AWS, ECR, Docker Hub e Terraform descritos na documentacao de deploy. O secret `FORWARD_ADDRESSES_JSON` deve ser uma lista JSON, por exemplo:

```json
["destino1@exemplo.com", "destino2@exemplo.com"]
```

## Estrutura principal

```text
src/forward_received_email/  Codigo da aplicacao
src/tests/                    Testes automatizados
infra/                        Infraestrutura Terraform
docs/                         Documentacao operacional
.github/workflows/            CI/CD
Dockerfile                    Imagem do Lambda
```

## Documentacao

- [Arquitetura](docs/architecture.md)
- [Implantacao](docs/deployment.md)
