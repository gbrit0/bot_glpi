#! /bin/bash
cd /home/bot/glpi
while :
do
   cd /home/bot/glpi
   # Mata processos gunicorn
   pkill -f "gunicorn"
   printf "\n$(date) servidor bot inicializado\n"
   source venv/bin/activate
   gunicorn --bind 192.168.15.60:52001 -c gunicorn.config.py --timeout 60 api:app >> servidor.log
   printf "$(date) fim da execução do bot\n"
   sleep 5
done
