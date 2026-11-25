"""Reservas finitas da História. Ensaios de referência permitem recuperação."""
def limitado(j):
    return j.modo=='historia' and not hasattr(j,'sala_id') and not getattr(j,'ensaio_armas',False)


def descansar(j,o):
    if not limitado(j):
        cargas=min(j.bolsa.reserva_balsamo,max(0,j.bolsa.capacidade_balsamo-j.bolsa.estoque['balsamo']))
        if cargas:
            j.bolsa.reserva_balsamo-=cargas;j.bolsa.receber('balsamo',cargas)
        j.lume.energia=j.lume.vida=100.;j.eventos.append('coleta')
        j.notificar('Vida e brilho restaurados. '+j.objetivo,7.)
        return
    marca='descanso_'+o.id
    if (marca not in j.flags and j.lume.energia>=99.99 and j.lume.vida>=99.99
            and j.bolsa.estoque['balsamo']>=j.bolsa.capacidade_balsamo):
        j.notificar('Vida, brilho e bolsa cheios. A reserva continua guardada neste abrigo.',6.)
        return
    if marca in j.flags:
        if j.bolsa.reserva_balsamo and j.bolsa.estoque['balsamo']>=j.bolsa.capacidade_balsamo:
            j.notificar(f'Bolsa cheia. {j.bolsa.reserva_balsamo} bálsamo(s) continuam guardados no abrigo.',6.)
            return
        cargas=min(j.bolsa.reserva_balsamo,max(0,j.bolsa.capacidade_balsamo-j.bolsa.estoque['balsamo']))
        if cargas:
            j.bolsa.reserva_balsamo-=cargas
            j.bolsa.receber('balsamo',cargas)
            j.eventos.append('coleta')
            j.notificar(f'{cargas} bálsamo(s) retirado(s) da reserva. A luz atual não foi alterada.',6.)
            return
        j.notificar('Reserva esgotada. Bálsamo recupera vida/brilho; orvalho e acertos recuperam brilho. Marcos guardam retorno.',6.)
        return
    j.flags.add(marca)
    j.lume.energia=j.lume.vida=100.
    faltam=max(0,j.bolsa.capacidade_balsamo-j.bolsa.estoque['balsamo'])
    if faltam:j.bolsa.receber('balsamo',faltam)
    j.eventos.append('coleta')
    j.notificar(f'Reserva usada: vida/brilho cheios e {j.bolsa.capacidade_balsamo} bálsamos. Este abrigo não reabastece outra vez.',7.)


def iluminar_marco(j):
    # Pontos de retorno não fornecem cura repetível na campanha.
    if not limitado(j):j.lume.energia=j.lume.vida=100.
