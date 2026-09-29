import pytest
from datetime import datetime
from BarberTime.domain.model import barbeiro, Barbeiro, HorarioTrabalho, cliente, servico, Agendamento

def test_criar_barbeiro_com_horarios_padrao():
    b = barbeiro(id=1, nome="Jonathan")
    assert b.id == 1
    assert b.nome == "Jonathan"
    assert b.horario_inicio == "08:00"
    assert b.horario_fim == "18:00"
    assert b._obter_dias_trabalho() == [0, 1, 2, 3, 4, 5]

def test_criar_barbeiro_customizado():
    b = Barbeiro(id=2, nome="Carlos", horario_inicio="09:00", horario_fim="17:00", dias_trabalho=[0, 2, 4])
    assert b.horario_inicio == "09:00"
    assert b.horario_fim == "17:00"
    assert b._obter_dias_trabalho() == [0, 2, 4]

def test_horario_trabalho_value_object():
    ht = HorarioTrabalho(inicio="08:00", fim="18:00")
    assert ht.inicio == "08:00"
    assert ht.fim == "18:00"
    # Test checking times
    t_valido = datetime.strptime("10:00", "%H:%M").time()
    t_cedo = datetime.strptime("07:00", "%H:%M").time()
    t_tarde = datetime.strptime("19:00", "%H:%M").time()
    assert ht.contem_horario(t_valido, duracao_minutos=30) is True
    assert ht.contem_horario(t_cedo) is False
    assert ht.contem_horario(t_tarde) is False

def test_agendamento_dentro_do_horario_permitido():
    b = barbeiro(id=1, nome="Jonathan", horario_inicio="08:00", horario_fim="18:00")
    # Segunda-feira valida (2026-10-05 e uma segunda-feira)
    dt_valida = datetime(2026, 10, 5, 10, 0)
    assert b.pode_atender(dt_valida, duracao_minutos=45) is True
    # Nao lanca excecao
    b.validar_agendamento(dt_valida, duracao_minutos=45)

def test_impedir_agendamento_antes_do_inicio_do_expediente():
    b = barbeiro(id=1, nome="Jonathan", horario_inicio="08:00", horario_fim="18:00")
    dt_cedo = datetime(2026, 10, 5, 7, 30)
    assert b.pode_atender(dt_cedo) is False
    with pytest.raises(ValueError, match="antes do inicio do expediente"):
        b.validar_agendamento(dt_cedo)

def test_impedir_agendamento_apos_o_fim_do_expediente():
    b = barbeiro(id=1, nome="Jonathan", horario_inicio="08:00", horario_fim="18:00")
    dt_tarde = datetime(2026, 10, 5, 18, 30)
    assert b.pode_atender(dt_tarde) is False
    with pytest.raises(ValueError, match="apos o encerramento do expediente"):
        b.validar_agendamento(dt_tarde)

def test_impedir_agendamento_cuja_duracao_ultrapassa_o_expediente():
    b = barbeiro(id=1, nome="Jonathan", horario_inicio="08:00", horario_fim="18:00")
    # 17:45 com 30 minutos de duracao terminaria as 18:15 (apos as 18:00)
    dt_limite = datetime(2026, 10, 5, 17, 45)
    assert b.pode_atender(dt_limite, duracao_minutos=30) is False
    with pytest.raises(ValueError, match="ultrapassa o horario de encerramento"):
        b.validar_agendamento(dt_limite, duracao_minutos=30)

def test_impedir_agendamento_em_dia_nao_trabalhado():
    b = barbeiro(id=1, nome="Jonathan", dias_trabalho="0,1,2,3,4")  # Segunda a Sexta
    # 2026-10-11 e Domingo (weekday == 6)
    dt_domingo = datetime(2026, 10, 11, 10, 0)
    assert b.pode_atender(dt_domingo) is False
    with pytest.raises(ValueError, match="fora dos dias de trabalho"):
        b.validar_agendamento(dt_domingo)

def test_alterar_expediente_com_sucesso():
    b = barbeiro(id=1, nome="Jonathan", horario_inicio="08:00", horario_fim="18:00")
    b.alterar_expediente(novo_inicio="09:00", novo_fim="17:00")
    assert b.horario_inicio == "09:00"
    assert b.horario_fim == "17:00"

    # Horario das 08:30 nao deve mais ser aceito
    dt_antigo_valido = datetime(2026, 10, 5, 8, 30)
    assert b.pode_atender(dt_antigo_valido) is False

def test_alterar_expediente_invalido_rejeita():
    b = barbeiro(id=1, nome="Jonathan")
    with pytest.raises(ValueError, match="inicio deve ser anterior ao horario de fim"):
        b.alterar_expediente(novo_inicio="19:00", novo_fim="18:00")

def test_adicionar_agendamento_ao_barbeiro_valida_invariante():
    b = barbeiro(id=1, nome="Jonathan", horario_inicio="08:00", horario_fim="18:00")
    c = cliente(id=10, nome="Marcos")
    s = servico(id=1, nome="Corte", duracao=30, preco=50.0)

    # Agendamento valido
    agendamento_valido = Agendamento(
        id=1, cliente=c, barbeiro=b, servico=s, data_hora=datetime(2026, 10, 5, 14, 0)
    )
    b.adicionar_agendamento(agendamento_valido)

    # Agendamento fora do expediente
    agendamento_invalido = Agendamento(
        id=2, cliente=c, barbeiro=b, servico=s, data_hora=datetime(2026, 10, 5, 19, 0)
    )
    with pytest.raises(ValueError, match="apos o encerramento do expediente"):
        b.adicionar_agendamento(agendamento_invalido)

def test_igualdade_de_barbeiros_por_identidade():
    b1 = barbeiro(id=1, nome="Jonathan", horario_inicio="08:00", horario_fim="18:00")
    b2 = barbeiro(id=1, nome="Jonathan Silva", horario_inicio="09:00", horario_fim="17:00")
    b3 = barbeiro(id=2, nome="Jonathan")
    assert b1 == b2
    assert b1 != b3
    assert hash(b1) == hash(b2)
