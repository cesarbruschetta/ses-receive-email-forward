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

O Lambda usa uma imagem hospedada no Amazon ECR, que é obrigatório para funções Lambda baseadas em imagem. O workflow de deploy publica a imagem no ECR automaticamente.

```bash
export AWS_REGION="us-east-1"
export AWS_ACCOUNT_ID="123456789012"
export IMAGE_NAME="ses-email-forwarder"
export TAG="v1.0.0"

# Cria o repositório (se ainda não existir)
aws ecr describe-repositories --repository-names ${IMAGE_NAME} >/dev/null 2>&1 || \
  aws ecr create-repository --repository-name ${IMAGE_NAME}

# Autentica o Docker no ECR
aws ecr get-login-password --region ${AWS_REGION} | \
  docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

docker build -t ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${IMAGE_NAME}:${TAG} .
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${IMAGE_NAME}:${TAG}
```

No GitHub Actions, configure os secrets `FORWARD_ADDRESSES_JSON`, `SES_RECIPIENT_ADDRESSES_JSON` e `FROM_ADDRESS`. O `FORWARD_ADDRESSES_JSON` é uma lista JSON, por exemplo `["[EMAIL]"]`. O repositório ECR é criado automaticamente pelo workflow no primeiro deploy.

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

### Permissões IAM necessárias

A credencial AWS usada pelo Terraform (o usuário/role por trás de `AWS_ACCESS_KEY_ID` e `[ADDRESS]`) precisa das permissões abaixo. Uma policy pronta está em [`infra/deployer-iam-policy.json`](../infra/deployer-iam-policy.json).

| Serviço | Permissões | Motivo |
| --- | --- | --- |
| S3 | `s3:CreateBucket`, `s3:DeleteBucket`, `s3:GetBucket*`, `s3:PutBucketPolicy`, `s3:PutBucketPublicAccessBlock`, `s3:PutBucketTagging`, `s3:DeleteObject` | Criar o bucket de e-mails, policy e public access block |
| S3 (backend) | `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject`, `s3:ListBucket` | Ler/escrever o state remoto |
| ECR | `ecr:CreateRepository`, `ecr:DeleteRepository`, `ecr:DescribeRepositories`, `ecr:GetLifecyclePolicy`, `ecr:PutLifecyclePolicy`, `ecr:DeleteLifecyclePolicy`, `ecr:GetRepositoryPolicy`, `ecr:SetRepositoryPolicy`, `ecr:DeleteRepositoryPolicy`, `ecr:TagResource` | Criar o repositório da imagem do Lambda e sua lifecycle policy |
| SNS | `sns:CreateTopic`, `sns:DeleteTopic`, `sns:GetTopicAttributes`, `sns:SetTopicAttributes`, `sns:Subscribe`, `sns:Unsubscribe`, `sns:GetSubscriptionAttributes`, `sns:SetSubscriptionAttributes` | Criar tópico, policy e assinatura do Lambda |
| SES | `ses:CreateReceiptRuleSet`, `ses:DeleteReceiptRuleSet`, `ses:DescribeReceiptRuleSet`, `ses:CreateReceiptRule`, `ses:DeleteReceiptRule`, `ses:DescribeReceiptRule`, `ses:UpdateReceiptRule`, `ses:SetActiveReceiptRuleSet`, `ses:DescribeActiveReceiptRuleSet` | Criar/ativar o receipt rule set e a rule |
| Lambda | `lambda:CreateFunction`, `lambda:DeleteFunction`, `lambda:GetFunction*`, `lambda:UpdateFunctionCode`, `lambda:UpdateFunctionConfiguration`, `lambda:AddPermission`, `lambda:RemovePermission`, `lambda:GetPolicy`, `lambda:TagResource` | Criar a função, permissão de invocação e tags |
| CloudWatch Logs | `logs:CreateLogGroup`, `logs:DeleteLogGroup`, `logs:DescribeLogGroups`, `logs:PutRetentionPolicy`, `logs:TagResource` | Criar o log group e definir retenção |
| IAM | `iam:CreateRole`, `iam:DeleteRole`, `iam:GetRole`, `iam:CreatePolicy`, `iam:DeletePolicy`, `iam:GetPolicy*`, `iam:CreatePolicyVersion`, `iam:AttachRolePolicy`, `iam:DetachRolePolicy`, `iam:PassRole` | Criar a role/policy do Lambda e passá-la à função |
| STS | `sts:GetCallerIdentity` | Usado pelo provider AWS |

> O `iam:PassRole` deve ser restrito à role do Lambda (`ses-email-forwarder-lambda-role`) com a condição `iam:PassedToService = lambda.amazonaws.com`.

Para criar a policy e anexá-la ao usuário de deploy:

```bash
aws iam create-policy \
  --policy-name ses-email-forwarder-deployer \
  --policy-document file://infra/deployer-iam-policy.json

aws iam attach-user-policy \
  --user-name SEU_USUARIO_DE_DEPLOY \
  --policy-arn arn:aws:iam::SEU_ACCOUNT_ID:policy/ses-email-forwarder-deployer
```

> Ajuste `SEU_BUCKET_DE_STATE` e o nome do bucket de e-mails (`ses-email-forwarder-mail-receipts`) na policy conforme o seu `project_name`.

### Múltiplos domínios e destinatários

Para receber em vários domínios e encaminhar para vários endereços, basta preencher as listas:

```hcl
ses_recipient_addresses = ["domain1.com", "domain2.com"]
forward_addresses       = ["[EMAIL]", "[EMAIL]"]
from_address            = "AWS Forward <no-reply@%s>"
```

O `%s` em `from_address` é opcional e é substituído pelo domínio que recebeu a mensagem.
