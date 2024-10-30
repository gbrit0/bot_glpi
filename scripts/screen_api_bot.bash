#! /bin/bash
screen -XS api_bot quit
screen -dmS api_bot
screen -S api-bot -p 0 -X stuff 'bash /home/bot/glpi/scripts/servidor_api_bot.bash
'