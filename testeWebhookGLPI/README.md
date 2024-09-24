# Teste do Webhook GLPI

Webhook disponibilizado na biblioteca do GLPI e com documentação disponível [aqui.](https://github.com/ericferon/glpi-webhook/wiki/Webhook)

O Webhook fas operações de POST e PUT em um dado endereço. Para fins de teste criou-se uma pequena API usando Flask que recebe as atualizações configuradas no GLPI e as imprime.

Os dados enviados via API são escolhidos pelas tags disponíveis dentro da página de configuração. <s>Existem alguns modelos pré configurados que podem ser adotados, vou estudá-los.</s> Os modelos pré configurados não se aplicam às requisições https adotadas. Sua formatação é incompatível de modo que criei uma que atende às necessidades do Bot. Essa formatação pode ser encontrada [aqui](/testeWebhookGLPI/formatarjsons.json).

