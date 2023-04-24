# PRACTICA-2

Para esta práctica se aportan 3 archivos :
1) La versión básica

Esta versión contiene la solución inicial que únicamente garantiza la seguridad del puente. Esto se consigue mediante el uso de las variables condición, considerando la condición de que un coche que se dirige en una dirección no puede acceder al puente si hay peatones o coches que se dirigen en la otra dirección. El problema de esta solución es que puede generarse inanición y/o deadlock.

2) La versión final

Esta versión es la que se considera "correcta".Mediante la incorporación de las variables wait que se refieren al número de coches (N/S) o peatones que se encuetran esperando a entrar en el puente. Si no consideramos más modificaciones entonces se soluciona la inanición pero podría producirse deadlock (situación donde podría darse deadlock explicado en el archivo pdf).Para solucionar esto último incorporamos al código una variable "turno" que se encarga de controlar quien tiene acceso al puente.

4) La demostración de que la solución final no genera problemas.

En este archivo se explica partiendo de la solución "básica" los problemas que esta genera y como mediante las correspondientes modificaciones se va eliminando todos los posibles problemas hasta llegar a la versión final.


