# Bot Whatsapp para o GLPI

### Bot desenvolvido para notificação dos autores a cada atualização em seus chamados para aumentar o nível de interação dos usuários com a equipe técnica e capturar de maneira mais fácil a aprovação/recusa de uma solução.

---

Projeto desenvolvido em conformidade com o [levantamento de requisitos](/levantamentoDeRequisitos/levantamentoDeRequisitos.md) no qual se definiram os objetivos do bot e a estrutura inicial foi pensada.

## Implementação
A implementação da solução pode ser dividida em duas partes: 
* Implementação no ambiente GLPI
* Implementação do backend


### Implementação no ambiente GLPI
1. Instalação do plugin: 

* Acessar a aba de plugins do GLPI:

![Na tela inicial do GLPI, acessar Configurações > Plug-ins](/assets/1.png)

* No Marketplace, acessar 'Descoberta' e pesquisar por 'Webhook'. Instalar e ativar o plug-in:

![Marketplace > Descoberta > Pesquisar por 'Webhook'](/assets/2.png)

* Conceder autorizações para os perfis de usuários desejados:

![Administração > Perfis. Escolher um perfil de usuário e clicar sobre o nome do perfil](/assets/3.png)

![Dentro do perfil, acessar Webhooks Config e conceder todas as permissões](/assets/4.png)

2. Personalização do webhook para o bot: 

* Com as autorizações concedidas, acessar a aba Webhook, dentro de Configurações, e adicionar um novo webhook:

![Criar um novo webhook](/assets/5.png)

Configurar conforme imagem e salvar:

![Configurar conforme imagem](/assets/6.png)

* Habilitar as notificações via Webhook:

![Habilitar as notificações via Webhook](/assets/7.png)

* Configurar o modelo de notificação:

![Configurar o modelo de notificação](/assets/8.png)

Adicionar novo modelo, nomear, definir o tipo como 'Chamado' e salvar. Após salvar, será redirecionado para a página de tradução do modelo:

![Configurar o modelo de notificação](/assets/9.png)

Preencher o corpo do texto do e-mail com o conteúdo de [modelo de notificação geral](modelo.json). Corpo de texto HTML do e-mail deve ser preenchido apenas com '{}. Salvar.

* Configurar as notificações:

![Acessar a aba de notificações](/assets/10.png)

Criar a notificação conforme imagem abaixo:

![Criar a notificação](/assets/11.png)

Adicionar um novo modelo

![Adicionar um modelo](/assets/12.png)

Em 'Modo' selecionar Webhook e em 'Modelo de notificação' selecionar o modelo criado anteriormente. Adicionar.

![Selecionar um modelo](/assets/13.png)

Selecionar o Webhook como destinatário e atualizar:

![Selecionar o Webhook como destinatário](/assets/14.png)

Adicionar novas notificações, seguindo os mesmos passos, para os seguintes eventos:

   * Atualização de um chamado
   * Chamado solucionado
   * Novo acompanhamento
   * Novo chamado

Neste ponto, a configuração do Webhook para o Bot estará concluída.

Os passos para configuração do plug-in também estão disponíveis na [documentação do projeto](https://github.com/ericferon/glpi-webhook/wiki/Webhook).



### Implementação do backend

A execução do backend do bot depende da Evolution API, da API do GLPI, da [API do projeto](api.py) e das bibliotecas em [requirements.txt](requirements.txt).

#### Evolution API: 
A instalação da Evolution ocorreu por meio do docker, conforme a [documentação do projeto](https://doc.evolution-api.com/v2/pt/install/docker) a partir do [docker-compose](docker-compose.yaml).

Após a instalação, acessar o Evolution Manager e criar uma nova instância. Na criação da instância, será gerada uma API Key (api_key) que usaremos adiante. Também será gerado um QR Code que deve ser lido pelo Whatsapp do qual se deseja enviar as mensagens. 

![Criação de uma nova instância no Evolution Manager](/assets/18.png)

Com a instância criada, configurar conforme imagem a seguir. Note que a URL do Webhook pode mudar dependendo do servidor onde está sendo executada a API do projeto. O endpoint será sempre o '/answers' porém o endereço pode variar. Deve ser o IP da máquina onde se executa a API do projeto.

![Configuração da instância da Evolution](/assets/19.png)

As demais opções não precisam ser habilitadas.

#### API do GLPI:

É necessário ativar a API do GLPI para que esta receba as recusas/aprovações de chamados:

Após configurar 4 como na imagem a seguir, adicione um novo cliente de API em 5

![Ativar a API](/assets/15.png)

Exemplo de cadastro de um novo cliente:

![Exemplo de cadastro de um novo cliente API](/assets/16.png)

O mais importante nesse cadastro é o Token da aplicação (app_token) que será gerado ao cadastrar um novo usuário. Ele é um requisito para acessar a API do GLPI.

Precisamos também de um API token. Originalmente o usuário 'ti' forneceu o api token. A informação pode ser encontrada no cadastro de usuários (Administração > Usuários) em 'Chaves de acesso remoto', conforme exemplo:

![API token](/assets/17.png)



#### API do projeto:

A API do projeto foi escrita em flask e o servidor WSGI utilizado é o gunicorn.

A inicialiação do serviço é feita em uma screen chamando o [script de incialização](/scripts/servidor_api_bot.bash):

      bash scripts/servidor_api_bot.bash 

A inicialização de fato do servidor vem de:

      gunicorn --bind 192.168.15.60:52001 -c gunicorn.config.py --timeout 60 api:app >> servidor.log

em que gunicorn.config.py é o arquivo em que são definidas as variáveis de ambiente necessárias para execução da API. Seu conteúdo deve ser:

~~~python
import os

os.environ['GLPI_API_BASE_URL'] = 'https://brggeradores.com.br/glpi/apirest.php/'
os.environ['GLPI_APP_TOKEN'] = "<app_token>"
os.environ['GLPI_AUTH'] = "user_token <api_token>"
os.environ['EVOLUTION_API_BASE_URL'] = "http://192.168.15.60:8080"
os.environ['EVOLUTION_API_KEY'] = "<evolution api_key>"
os.environ['GLPI_MYSQL_USER']="<user>" 
os.environ['GLPI_MYSQL_PASSWORD']="<password>"
os.environ['GLPI_MYSQL_HOST']="<host>"
os.environ['GLPI_MYSQL_DATABASE']="glpi"
~~~

Para garantir a execução da API em caso de reinicialização do sistema, defini-se um [script de screen](/scripts/screen_api_bot.bash) que realiza a chamada do script de inicialização dentro de uma screen. O script da screen, por sua vez, deve ser chamado via crontab:

1. Acessar o crontab do sistema via
      ~~~
      crontab -e
      ~~~

2. Adicionar o conteúdo
      ~~~
      @reboot sleep 60 && /bin/bash /home/bot/glpi/scripts/screen_api_bot.bash >> /home/bot/glpi/crontab.log 2>&1
      ~~~


































