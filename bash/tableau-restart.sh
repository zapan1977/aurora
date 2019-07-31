#!/bin/sh

# tsm path
Tableau_TSM=""
# Bach 변수에서 Tableau User / Password 가져와서 restart
${Tableau_TSM} restart \
--username $Tableau_ID \
--password $Tableau_PWD
