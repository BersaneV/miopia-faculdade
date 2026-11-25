"""A veneziana e os sinais de evacuação no Arquivo da Casca."""
import pygame

from .fases import Objeto

AREA = pygame.Rect(63, 1065, 343, 217)
PISO = 1173
PUXADORES = (224, 365)
SINAIS = (328, 1148)
FECHADA = 'veneziana_arquivo_fechada'
LIDOS = 'arquivo_sinais_lidos'
CONFIRMADOS = 'arquivo_sinais_confirmados'
ENTREGUES = 'arquivo_sinais_entregues'


def objetos(j):
    fechada = FECHADA in j.cartografia
    nome = 'Reabrir a veneziana' if fechada else 'Fechar a veneziana'
    oeste, leste = PUXADORES
    puxadores = (Objeto('veneziana_oeste', 'veneziana', oeste, PISO, nome),
                 Objeto('veneziana_leste', 'veneziana', leste, PISO, nome))
    if fechada:
        return (*puxadores, Objeto('sinais_arquivo', 'sinal_arquivo', SINAIS[0], PISO, 'Ler os traços na parede'))
    return puxadores


def luzes(j):
    if j.lume.rect.bottom > PISO or not AREA.collidepoint(j.lume.rect.center):
        return ()
    foco = (*SINAIS, 50) if FECHADA in j.cartografia else (279, 1121, 82)
    return (foco, *((x, PISO-27, 30) for x in PUXADORES))


def interagir(j, o):
    memoria = j.cartografia
    if o.tipo == 'sinal_arquivo':
        if FECHADA not in memoria:
            return
        memoria.add(LIDOS)
        j.dialogo = ('Os sinais sob a veneziana',
                     'Dois traços curtos e um longo. O orvalho seco ainda brilha nos riscos. '
                     'Reabra a veneziana para comparar com o facho. Véspera conhece os sinais dos ninhos altos.')
        j.memorizar(*j.dialogo)
        j.eventos.append('pagina')
        return

    if FECHADA in memoria:
        memoria.remove(FECHADA)
        if LIDOS in memoria and CONFIRMADOS not in memoria:
            memoria.add(CONFIRMADOS)
            j.notificar('O facho encobre os traços. Conte a Véspera, nos ninhos altos do Bosque.', 7.)
        else:
            j.notificar('O facho voltou à parede.')
    else:
        memoria.add(FECHADA)
        j.notificar('O facho se apagou. Os traços aparecem na parede à direita.', 6.)
    j.eventos.append('madeira')


def entregar_a_vespera(j):
    if CONFIRMADOS not in j.cartografia or ENTREGUES in j.cartografia:
        return ''
    j.cartografia.add(ENTREGUES)
    j.bolsa.receber('casulo', 1)
    j.eventos.append('coleta')
    texto = ('Dois curtos e um longo. Fio respondia da galeria. Eu ficava no galho alto '
             'contando os pequenos. Quando ela mostrou o último traço, soube que o caminho '
             'estava livre. Leve este Casulo de seda. Ele segura um golpe.')
    j.memorizar('O sinal de Fio · Véspera', texto)
    return texto
