# Implantação

## Requisitos

- Python 3.13
- Poetry
- Docker
- Terraform
- Conta AWS com permissões para SES, S3, SNS, IAM e Lambda
- Amazon ECR habilitado na conta AWS

## Build local

```bash
poetry install --with dev
poetry run pytest

docker build -t ses-email-forwarder:local .
```

## Publicar imagem

O Lambda usa uma imagem hospedada no Amazon ECR, que é obrigatório para funções Lambda baseadas em imagem. O workflow também pode publicar uma cópia no Docker Hub para distribuição externa.

```bash
export DOCKERHUB_USERNAME="seu_usuario"
export IMAGE_NAME="ses-email-forwarder"
export TAG="v1.0.0"


docker build -t ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${TAG} .
docker push ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${TAG}
```

No GitHub Actions, configure `FORWARD_ADDRESSES_JSON` como JSON, por exemplo `["destino@exemplo.com"]`. O repositório ECR é criado pelo primeiro deploy.

## Terraform

1. Crie o bucket S3 do backend manualmente.
2. Ajuste os valores do arquivo `infra/terraform.tfvars.example`.
3. Inicialize o backend e aplique:

```bash
cd infra
terraform init -backend-config="bucket=SEU_BUCKET" -backend-config="key=ses-forwarder/terraform.tfstate" -backend-config="region=us-east-1" -backend-config="encrypt=true"
terraform plan
terraform apply
```

> O apply do Terraform é executado no workflow somente quando uma tag GitHub é criada.

### Múltiplos domínios e destinatários

Para receber em vários domínios e encaminhar para vários endereços, basta preencher as listas:

```hcl
ses_recipient_addresses = ["domain1.com", "domain2.com"]
forward_addresses       = ["[EMAIL]", "[EMAIL]"]
from_address            = "AWS Forward <no-reply@%s>"
```

O `%s` em `from_address` é opcional e é substituído pelo domínio que recebeu a mensagem.
