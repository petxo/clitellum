Clitellum
=========

## Introducción

Es un framework de comunicación que es capaz de utilizar conectores tcp, amqp y zeromq, indistintamente. Puede ser usado para implementar publicadores de eventos, suscriptores de eventos, intercambiadores de protocolo, etc.

Implementa patrones de diseños empresariales como el “Reliable Endpoint”, que en caso de producirse un pérdida de conexión, el propio endpoint es capaz de volverse a conectar, tantas veces como sea necesario, ya sea para recibir un mensaje como para enviarlo. O patrones como el “Dead Letter Channel”, que en caso de producirse un error durante el procesamiento del mensaje, se envía el mensaje a un endpoint de errores, para que sea investigado.

Por esto, es muy útil para implementar microservicios en python, o intercambiadores de protocolo, ya que los endpoints de entrada y salida pueden ser de tipos diferentes.

Mas información en la wiki

https://github.com/petxo/clitellum/wiki
