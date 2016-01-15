from clitellum.core.queue import FileQueue

__author__ = 'sergio'

fq = FileQueue('queue.db')

fq.append("Hola Mundo")

msg = fq.popleft()

print msg
