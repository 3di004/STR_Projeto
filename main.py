import threading
import time
import random

# CONFIGURAÇÕES DO SISTEMA 
CAPACIDADE_PATIO = 2  # Buffer limitado 
vagas_patio = threading.Semaphore(CAPACIDADE_PATIO)  # Controla o espaço no buffer
trilho_compartilhado = threading.Semaphore(1)        # Mutex para o recurso único 

# Contador interno do pátio para fins de exibição na tela
total_no_patio = 0
trava_print = threading.Lock() # Evita que os prints se misturem na tela

def print_status(mensagem):
    """Garante que a saída do terminal seja limpa e organizada """
    with trava_print:
        print(mensagem)

def trem_produtor(linha_id):
    """Thread que representa os Trens das Linhas 1, 2 e 3 """
    global total_no_patio
    
    while True:
        # 1. Simula o tempo de carregamento na mina (Ajustado para o fluxo de 3 trens)
        time.sleep(random.uniform(5.0, 10.0))
        print_status(f"[Linha {linha_id}] Trem carregado e pronto para partir.""" )
        print_status(f"[Linha {linha_id}] Solicitando trilho...""")

        # Passo A: Solicita acesso ao recurso compartilhado (Trilho Único)
        trilho_compartilhado.acquire()
        print_status(f"[Trilho] Trem da Linha {linha_id} entrou no trilho compartilhado.")

        # 2. Tempo de travessia mantido exatamente em 3.2 segundos
        time.sleep(3.2)

        print_status(f"[Trilho] Trem da Linha {linha_id} chegou ao fim do trilho.")
        print_status(f"[Linha {linha_id}] Aguardando no pátio...""")
        # Passo B: Tenta descarregar no Pátio (Buffer)
        # (Se o pátio estiver cheio, causará o DEADLOCK pedido no PDF 1 aqui)
        vagas_patio.acquire() 

        # Atualiza o buffer
        total_no_patio += 1
        print_status(f"[PÁTIO] Trem da Linha {linha_id} DESCARREGOU. Vagas ocupadas: {total_no_patio}/{CAPACIDADE_PATIO}")
        print_status(f"[PÁTIO] Vagas ocupadas: {total_no_patio}/{CAPACIDADE_PATIO}""")
        # Libera o trilho compartilhado para o próximo trem
        trilho_compartilhado.release()
        print_status(f"[Trilho] Trem da Linha {linha_id} LIBEROU o trilho compartilhado.")

def agente_descarregador():
    """Thread que remove os itens do pátio (Equivalente ao Agente Externo do PDF 1)"""
    global total_no_patio
    
    while True:
        # O pátio é esvaziado de forma assíncrona por um operador externo
        time.sleep(random.uniform(6.0, 10.0)) 
        
        with trava_print:
            if total_no_patio > 0:
                total_no_patio -= 1
                print(f"--> [AGENTE EXTERNO] Retirou uma carga do pátio. Vagas ocupadas: {total_no_patio}/{CAPACIDADE_PATIO}")
                vagas_patio.release() # Libera uma vaga no semáforo do buffer
            else:
                print("--> [AGENTE EXTERNO] Pátio vazio, nada para retirar.")

# --- INICIALIZAÇÃO DO SISTEMA ---
if __name__ == "__main__":
    print_status("[SISTEMA] Iniciando Cruzamento Ferroviário Inteligente (3 Trens)...")
    
    # Criando as threads para os 3 trens usando uma lista (Mais limpo e escalável)
    trens = []
    for i in range(1, 4):  # Gera as linhas 1, 2 e 3
        t = threading.Thread(target=trem_produtor, args=(i,), name=f"Trem_Linha_{i}")
        trens.append(t)
    
    # Criando a thread de esvaziamento do buffer
    operador = threading.Thread(target=agente_descarregador, name="Agente_Externo", daemon=True)

    # Iniciando todos os processos de tempo real
    for trem in trens:
        trem.start()
        
    operador.start()