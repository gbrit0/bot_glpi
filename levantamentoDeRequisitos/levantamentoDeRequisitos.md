# Levantamento de Requisitos para o Projeto de Bot com o GLPI

## Coleta de Requisitos:
#### Objetivos do projeto:
   * Qual é o principal objetivo do bot?
   
      Fornecer aos usuários (funcionários que usam o GLPI para chamados relacionados ao Protheus) informações sobre o andamento de seus chamados.

   * Quais problemas o bot deve resolver?

      Ausência de feedback por parte dos usuários quanto à solução dos chamados.

   * Quais são as metas de negócios que precisam ser alcançadas?
      * Melhoria da Comunicação Interna
      * Melhoria de Experiência do Usuário
      * Redução de Tempo de Resolução de Chamados

#### Requisitos Funcionais:
   * O que o bot deve fazer?
      * Notificar o usuário via WhatsApp sempre que houverem atualizações em seu chamado. <s>Notificar o usuário via WhatsApp quando seu chamado for solucionado</s>
      * Permitir aceitar ou negar uma solução de chamado

   * Quais funcionalidades principais o bot deve oferecer?
      * Envio de mensagens
      * Interação via botões

   * Como os usuários irão interagir com o sistema?
      * Recebendo mensagens no WhatsApp
      * Aceitar ou negar uma solução de chamado

   * Quais são as entradas necessárias e quais saídas são esperadas?
      * Entradas: todas as atualizações em um chamado desde a abertura até sua conclusão <s>soluções em um chamado</s>, número de telefone dos usuários (GLPI possui o campo mas acredito que não seja preenchido);
      * Saídas: mensagens no WhatsApp do autor do chamado
   
#### Requisitos não funcionais:
   * Quais os requisitos de desempenho do sistema (velocidade, tempo de resposta)?

   * Qual o nível de disponibilidade esperado (horário de funcionamento, tempo de inatividade tolerável)?   
   
#### Usuários e Stakeholders:
   * Quem usará o sistema (tipos de usuários, níveis de acesso)?
      * Usuários Self-Service do GLPI: Acesso padrão para receber as notificações

   * Quem são os principais stakeholders e como eles se relacionam com o sistema?
      * Funcionários - Usam o GLPI para chamados relacionados ao Protheus (clientes internos);
      * Time de desenvolvimento Protheus - prestador de serviço;
      * Giuliana - Controladoria;
      * Desenvolvimento - Desenvolver e manter o Bot
   
#### Processos e Fluxo de Trabalho:
   * Quais são os processos atuais que o sistema precisa automatizar ou melhorar?
      * Acesso dos usuários às notificações do GLPI
   * Como os fluxos de trabalho funcionam atualmente?
      * O usuário abre o sistema, seleciona o chamado e visualiza as mensagens

   * Existem processos manuais que precisam ser transformados em automáticos?
      * Acesso ao sistema para acompanhar notificações

   * Existem interações específicas com outros sistemas?
      * Coleta de dados do GLPI via Webhook
      * Envia de mensagens para a API do WhatsApp via Evolution e Typebot

#### Integrações e Interoperabilidade:
   * Quais sistemas precisam ser integrados a este novo sistema?
      * GLPI
      * WhatsApp
      * TypeBot
      * Evolution
      * <s>Chatwoot</s>
      * Webhook

   * Que tipo de dados será trocado entre os sistemas?
      * Exclusivamente mensagens de texto


#### Dados e Armazenamento:
   * Que tipo de dados o sistema deve armazenar e processar?
      * <s>log de envio das mensagens?</s> O Typebot possui um registro
   
   * Como os dados devem ser organizados e apresentados aos usuários?
      * Template de mensagem WhatsApp