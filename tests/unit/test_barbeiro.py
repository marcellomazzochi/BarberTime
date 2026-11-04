import pytest
from datetime import datetime
from BarberTime.domain.model import barbeiro, Barbeiro, HorarioTrabalho, JornadaTrabalho, cliente, servico, Agendamento

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

def test_jornada_trabalho_isolada_value_object():
    jornada = JornadaTrabalho(horario_inicio="09:00", horario_fim="18:00", dias_trabalho="0,1,2,3,4")
    assert jornada.obter_dias() == [0, 1, 2, 3, 4]

    # Segunda-feira as 10h (dentro)
    dt_valida = datetime(2026, 10, 5, 10, 0)
    assert jornada.contem_dia(dt_valida) is True
    assert jornada.contem_horario(dt_valida, duracao_minutos=30) is True
    jornada.validar_atendimento(dt_valida, duracao_minutos=30)

    # Domingo (fora dos dias de trabalho)
    dt_domingo = datetime(2026, 10, 11, 10, 0)
    assert jornada.contem_dia(dt_domingo) is False
    assert jornada.contem_horario(dt_domingo) is False
    with pytest.raises(ValueError, match="fora dos dias de trabalho"):
        jornada.validar_atendimento(dt_domingo)

    # Horario antes do inicio
    dt_antes = datetime(2026, 10, 5, 8, 30)
    assert jornada.contem_horario(dt_antes) is False
    with pytest.raises(ValueError, match="antes do inicio do expediente"):
        jornada.validar_atendimento(dt_antes)

    # Horario apos o fim
    dt_depois = datetime(2026, 10, 5, 18, 30)
    assert jornada.contem_horario(dt_depois) is False
    with pytest.raises(ValueError, match="apos o encerramento do expediente"):
        jornada.validar_atendimento(dt_depois)

    # Duracao que ultrapassa o encerramento
    dt_limite = datetime(2026, 10, 5, 17, 45)
    assert jornada.contem_horario(dt_limite, duracao_minutos=30) is False
    with pytest.raises(ValueError, match="ultrapassa o horario de encerramento"):
        jornada.validar_atendimento(dt_limite, duracao_minutos=30)


def test_jornada_trabalho_com_novo_expediente_imutavel():
    jornada = JornadaTrabalho(horario_inicio="08:00", horario_fim="18:00")
    nova = jornada.com_novo_expediente("10:00", "19:00")
    assert jornada.horario_inicio == "08:00"
    assert nova.horario_inicio == "10:00"
    assert nova.horario_fim == "19:00"

    with pytest.raises(ValueError, match="inicio deve ser anterior ao horario de fim"):
        jornada.com_novo_expediente("19:00", "18:00")


def test_barbeiro_com_jornada_injetada_srp():
    jornada_custom = JornadaTrabalho(horario_inicio="13:00", horario_fim="21:00", dias_trabalho="1,2,3,4,5")
    b = barbeiro(id=5, nome="Lucas", jornada=jornada_custom)
    assert b.horario_inicio == "13:00"
    assert b.horario_fim == "21:00"
    assert b.jornada == jornada_custom

    # 10:00 esta fora da jornada deste barbeiro
    dt_manha = datetime(2026, 10, 6, 10, 0)
    assert b.pode_atender(dt_manha) is False

    # 15:00 esta dentro
    dt_tarde = datetime(2026, 10, 6, 15, 0)
    assert b.pode_atender(dt_tarde) is True


def test_barbeiro_definir_nova_jornada_dinamica():
    b = barbeiro(id=1, nome="Jonathan")
    nova_jornada = JornadaTrabalho(horario_inicio="07:00", horario_fim="15:00", dias_trabalho="0,1,2,3,4")
    b.definir_jornada(nova_jornada)
    assert b.horario_inicio == "07:00"
    assert b.horario_fim == "15:00"
    assert b.jornada == nova_jornada

    # 07:30 agora e valido
    dt_cedo = datetime(2026, 10, 5, 7, 30)
    assert b.pode_atender(dt_cedo) is True

