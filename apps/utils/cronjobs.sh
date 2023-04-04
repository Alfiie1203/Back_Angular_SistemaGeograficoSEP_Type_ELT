# Edit this file to introduce tasks to be run by cron.
# 
# Each task to run has to be defined through a single line
# indicating with different fields when the task will be run
# and what command to run for the task
# 
# This is the instaled task for proforest
#

#Task that updates the token for Onedrive every 55 minutes
*/55 * * * *  /home/proforest/virtualenv/bin/python3 /home/proforest/proforestpython/manage.py obtaintoken
#

#Generate Forms that updates every month
1 0 1 * * /home/proforest/virtualenv/bin/python3 /home/proforest/proforestpython/manage.py mensual_program_forms

#Generate bimensual forms
1 0 1 */2 * /home/proforest/virtualenv/bin/python3 /home/proforest/proforestpython/manage.py bimensual_program_forms

#Generate trimestral forms
1 0 1 */3 * /home/proforest/virtualenv/bin/python3 /home/proforest/proforestpython/manage.py trimestral_program_forms

#Generate Semestral forms
1 0 1 */6 * /home/proforest/virtualenv/bin/python3 /home/proforest/proforestpython/manage.py semestral_program_forms

#Generate Annual forms
1 0 1 */12 * /home/proforest/virtualenv/bin/python3 /home/proforest/proforestpython/manage.py anual_program_forms
#

#Close forms pending for Fill 
1 0 * * * /home/proforest/virtualenv/bin/python3 /home/proforest/proforestpython/manage.py finish_forms_for_fill

#Close forms pending for Validate 
1 0 * * * /home/proforest/virtualenv/bin/python3 /home/proforest/proforestpython/manage.py finish_forms_for_validate

#Close forms pending for Verificate 
1 0 * * * /home/proforest/virtualenv/bin/python3 /home/proforest/proforestpython/manage.py finish_forms_for_verificate

#Change status from not visible to active
1 0 * * * /home/proforest/virtualenv/bin/python3 /home/proforest/proforestpython/manage.py daily_update_status_form


