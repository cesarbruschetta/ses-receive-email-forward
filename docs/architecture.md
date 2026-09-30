# Arquitetura da solução

A aplicação recebe notificações do Amazon SES via SNS, lê o e-mail armazenado no S3 e reenvia para os destinatários configurados.

## Fluxo principal

1. O SES recebe o e-mail.
2. O SES grava o conteúdo no bucket S3 configurado.
3. O SES publica a notificação em um tópico SNS.
4. O Lambda executa a função `forward_received_email.lambda_function.lambda_handler`.
5. A função valida a origem, consulta a lista de remetentes bloqueados e reenvia o e-mail via SES.

## Componentes

- Lambda: processa eventos SNS
- S3: armazena o conteúdo do e-mail recebido
- SNS: dispara a notificação para o Lambda
- SES: envia o e-mail reencaminhado
- Docker: empacota a imagem do Lambda
- Terraform: provisiona infraestrutura AWS

## Variáveis de ambiente

- `FORWARD_ADDRESSES`: lista de e-mails de destino separados por vírgula
- `AWS_DEFAULT_REGION`: região AWS da aplicação
- `FROM_ADDRESS`: endereço de origem do e-mail reenviado
- `LOGGER_LEVEL`: nível de log da aplicação

## Múltiplos domínios e destinatários

A solução suporta vários domínios de recebimento e vários destinatários de encaminhamento ao mesmo tempo.

- **Recebimento**: a receipt rule do SES aceita uma lista de domínios/endereços em `ses_recipient_addresses`, por exemplo `["domain1.com", "domain2.com"]`.
- **Encaminhamento**: `FORWARD_ADDRESSES` é uma lista e é enviada diretamente em `ToAddresses`, então todos os endereços configurados recebem a mensagem.
- **Remetente**: `FROM_ADDRESS` pode conter o placeholder `%s`, que é substituído pelo domínio que recebeu a mensagem (ex.: `AWS Forward <no-reply@%s>`). Se o placeholder não existir, o endereço é usado como está.

O domínio usado no remetente é extraído do primeiro destinatário da mensagem recebida (`mail.destination[0]`).
