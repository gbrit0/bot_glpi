#! /bin/bash
screen -XS api_glpi quit
screen -dmS api_glpi
screen -S api_glpi -p 0 -X stuff 'bash /home/bot/glpi/scripts/servidor_api_bot.bash
'
