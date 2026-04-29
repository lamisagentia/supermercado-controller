#!/usr/bin/env python3
"""
Interface do Sistema de Controle de Supermercado
"""

import sys
sys.path.insert(0, '/root/supermercado')

from sistema import (
    init_system, registrar_compra, analisar_compra, 
    gerar_relatorio_mensal, load_data, save_data
)
from datetime import datetime
import json

def menu_principal():
    """Exibe menu principal"""
    print("\\n" + "="*50)
    print("🛒 SISTEMA DE CONTROLE DE SUPERMERCADO")
    print("="*50)
    print("1. 📸 Processar cupom (imagem)")
    print("2. ✍️  Lançar compra manualmente")
    print("3. 📊 Ver relatório mensal")
    print("4. 🔍 Consultar histórico de produto")
    print("5. 📈 Top 5 produtos mais comprados")
    print("0. Sair")
    print("="*50)

def lancar_compra_manual():
    """Permite lançar compra item por item"""
    print("\\n✍️  NOVA COMPRA")
    loja = input("Nome da loja: ").strip().upper() or "DESCONHECIDO"
    
    itens = []
    print("\\nDigite os itens (deixe vazio para finalizar):")
    
    while True:
        nome = input("\\n  Produto: ").strip()
        if not nome:
            if itens:
                break
            print("⚠️  Adicione pelo menos um item!")
            continue
        
        try:
            qtd = float(input("  Quantidade: ").replace(',', '.'))
            unitario = float(input("  Preço unitário (R$): ").replace(',', '.'))
        except ValueError:
            print("❌ Valor inválido!")
            continue
        
        total = qtd * unitario
        
        itens.append({
            'nome': nome,
            'qtd': qtd,
            'unitario': unitario,
            'total': total,
            'unidade': 'UN'
        })
        
        print(f"  ✅ {nome} x{qtd} = R$ {total:.2f}")
    
    # Registra compra
    compra = registrar_compra(itens, loja)
    print(f"\\n✅ Compra registrada! Total: R$ {compra['total']:.2f}")
    
    # Analisa
    analisar_compra(compra)

def consultar_produto():
    """Consulta histórico de um produto"""
    nome = input("\\n🔍 Nome do produto: ").strip().lower()
    
    produtos_db = load_data("produtos")
    
    if nome not in produtos_db["produtos"]:
        print("❌ Produto não encontrado no histórico.")
        return
    
    hist = produtos_db["produtos"][nome]
    
    print(f"\\n📊 HISTÓRICO: {nome.upper()}")
    print(f"Melhor preço: R$ {hist['melhor_preco']:.2f}")
    print(f"Loja: {hist.get('loja_melhor_preco', 'N/A')}")
    print(f"Registros: {len(hist['historico'])}")
    
    if hist['historico']:
        print("\\nÚltimas compras:")
        for reg in hist['historico'][-5:]:  # Últimas 5
            print(f"  • {reg['data'][:10]} | R$ {reg['preco_unit']:.2f} | {reg['loja']}")

def top_produtos():
    """Mostra top 5 produtos mais comprados"""
    produtos_db = load_data("produtos")
    
    if not produtos_db["produtos"]:
        print("❌ Nenhum produto registrado.")
        return
    
    # Conta frequência
    frequencia = {}
    for nome, dados in produtos_db["produtos"].items():
        qtd = len(dados.get('historico', []))
        if qtd > 0:
            frequencia[nome] = qtd
    
    if not frequencia:
        print("❌ Nenhum dado disponível.")
        return
    
    # Ordena e pega top 5
    top = sorted(frequencia.items(), key=lambda x: x[1], reverse=True)[:5]
    
    print("\\n🏆 TOP 5 PRODUTOS MAIS COMPRADOS:")
    for i, (nome, qtd) in enumerate(top, 1):
        print(f"  {i}. {nome.title()} ({qtd}x)")

def main():
    """Função principal"""
    init_system()
    
    while True:
        menu_principal()
        opcao = input("\\nEscolha uma opção: ").strip()
        
        if opcao == '1':
            print("\\n📸 Envie a imagem do cupom (em breve com OCR)")
            print("⚠️  No momento, use a opção 2 para lançamento manual.")
        elif opcao == '2':
            lancar_compra_manual()
        elif opcao == '3':
            gerar_relatorio_mensal()
        elif opcao == '4':
            consultar_produto()
        elif opcao == '5':
            top_produtos()
        elif opcao == '0':
            print("\\n👋 Até mais!")
            break
        else:
            print("❌ Opção inválida!")

if __name__ == "__main__":
    main()
