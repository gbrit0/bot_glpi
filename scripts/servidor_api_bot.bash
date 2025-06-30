#! /bin/zsh
cd /home/gabriel/bot_glpi
while :
do
   cd /home/gabriel/bot_glpi
   # Mata processos gunicorn
   pkill -f "/home/gabriel/bot_glpi/venv/bin/gunicorn"
   printf "\n$(date) servidor bot inicializado\n"
   source venv/bin/activate
   gunicorn --bind 172.49.49.6:52001 -c gunicorn.config.py --timeout 60 api:app >> servidor.log
   printf "$(date) fim da execução do bot\n"
   sleep 5
done
