# Convierte la exportación POSTGRES del esquema de SIGCAR a un sql que podemos
# importar en el MySQL Workbench.
#
# Para instalar el MySQL Workbench en Ubuntu:
# sudo snap install mysql-workbench-community
#
#Para extraer el esquema de la BBDD de Postgres:
# /usr/bin/pg_dump --file "/media/backup_ssv_accidentes/SIGCAR_esquema.sql" --host "127.0.0.1" --port "5432" --username "gvsig" --no-password --verbose --format=p --schema-only --no-owner --no-privileges --no-tablespaces --no-unlogged-table-data --no-comments "sigcar_MY_PRE"
# 
quote="'"
sed '1,55d
1,$s/NULL::character varying/NULL/ 
1,$s/NULL::numeric/NULL/ 
1,$s/'$quote'UNKNOWN'$quote'::character varying/'$quote'UNKNOWN'$quote'/
1,$s/ALTER SEQUENCE.*;//
1,$s/ALTER TABLE.*nextval.*;//
1,$s/USING "btree" //
1,$s/USING "gist" //
1,$s/^--.*//
1,$s/"public"."geometry"(.*)/BLOB/
1,$s/"date"/DATE/
1,$s/"text"/TEXT/
1,$s/time without time zone/TIME/
1,$s/"bytea"/BLOB/
1,$s/ALTER TABLE ONLY/ALTER TABLE/' /home/fdiaz/projects/backup_ssv_accidentes/SIGCAR_esquema.sql|tr '\n' ' ' | 
sed 's/;/;\n\n/g' | 
sed 's/CREATE SEQUENCE[^;]*;//g
s/CREATE VIEW[^;]*;//g
s/^.*"public"[.]"TRAMOS_CARRETERAS_20220527"[^;]*;//g
s/^.*"public"[.]"TRAMOS_CARRETERAS_2021_10_01"[^;]*;//g
s/^.*"public"[.]"TRAMOS_CARRETERAS_20220527_ORIGINAL"[^;]*;//g
s/^.*"public"[.]"TRAMOS_CARRETERAS_OLD"[^;]*;//g
s/^ *//
' | sed 's/,/,\n/g'

