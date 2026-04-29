#!/usr/bin/env python3
"""
Sistema de Controle de Gastos - Supermercado
Desenvolvido por: Lamis Agent
Finalidade: Controlar compras, comparar preços e sugerir economia
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Configurações
DATA_DIR = Path.home() / ".hermes" / "supermercado"
DB_FILE = DATA_DIR / "compras.json"
PRODUTOS_FILE = DATA_DIR / "produtos.json"

def init_system():
    """Inicializa o sistema e cria arquivos necessários"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    if not DB_FILE.exists():
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump({"compras": []}, f, indent=2, ensure_ascii=False)
    
    if not PRODUTOS_FILE.exists():
        with open(PRODUTOS_FILE, 'w', encoding='utf-8') as f:
            json.dump({"produtos": {}}, f, indent=2, ensure_ascii=False)
    
    print("✅ Sistema inicializado com sucesso!")

def load_data(file_type="compras"):
    """Carrega dados do arquivo JSON"""
    try:
        if file_type == "compras":
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            with open(PRODUTOS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        return {"compras": []} if file_type == "compras" else {"produtos": {}}

def save_data(data, file_type="compras"):
    """Salva dados no arquivo JSON"""
    try:
        if file_type == "compras":
            with open(DB_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            with open(PRODUTOS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar: {e}")
        return False

def registrar_compra(itens, loja="BISTEK", data=None):
    """Registra uma nova compra"""
    if data is None:
        data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    compra = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "data": data,
        "loja": loja,
        "itens": itens,
        "total": sum(item['total'] for item in itens),
        "qtd_itens": len(itens)
    }
    
    db = load_data("compras")
    db["compras"].append(compra)
    
    # Atualiza histórico de preços dos produtos
    produtos_db = load_data("produtos")
    for item in itens:
        nome = item['nome'].lower()
        if nome not in produtos_db["produtos"]:
            produtos_db["produtos"][nome] = {
                "historico": [],
                "melhor_preco": None,
                "loja_melhor_preco": None
            }
        
        produtos_db["produtos"][nome]["historico"].append({
            "data": data,
            "preco_unit": item['unitario'],
            "qtd": item['qtd'],
            "total": item['total'],
            "loja": loja,
            "unidade": item.get('unidade', 'UN')
        })
        
        # Atualiza melhor preço
        preco_unit = item['unitario']
        if (produtos_db["produtos"][nome]["melhor_preco"] is None or 
            preco_unit < produtos_db["produtos"][nome]["melhor_preco"]):
            produtos_db["produtos"][nome]["melhor_preco"] = preco_unit
            produtos_db["produtos"][nome]["loja_melhor_preco"] = loja
    
    save_data(db, "compras")
    save_data(produtos_db, "produtos")
    
    return compra

def analisar_compra(compra):
    """Analisa uma compra e gera insights"""
    print(f"\n{'='*60}")
    print(f"📊 ANÁLISE DA COMPRA - {compra['loja']}")
    print(f"Data: {compra['data']}")
    print(f"Total: R$ {compra['total']:.2f} ({compra['qtd_itens']} itens)")
    print(f"{'='*60}")
    
    # Carrega histórico
    produtos_db = load_data("produtos")
    
    economias = []
    alertas = []
    
    for item in compra['itens']:
        nome = item['nome'].lower()
        if nome in produtos_db["produtos"]:
            hist = produtos_db["produtos"][nome]
            melhor = hist["melhor_preco"]
            atual = item['unitario']
            
            if melhor and atual > melhor * 1.1:  # 10% mais caro
                economia = (atual - melhor) * item['qtd']
                economias.append({
                    'produto': item['nome'],
                    'pago': atual,
                    'melhor': melhor,
                    'economia_potencial': economia * item['qtd'],
                    'loja_melhor': hist.get('loja_melhor_preco', 'Desconhecida')
                })
    
    # Exibe resumo
    if economias:
        print("\n⚠️  PRODUTOS MAIS CAROS QUE O HABITUAL:")
        total_economia = 0
        for e in economias:
            print(f"  • {e['produto']}:")
            print(f"    Pago: R$ {e['pago']:.2f} | Melhor: R$ {e['melhor']:.2f}")
            print(f"    Economia potencial: R$ {e['economia_potencial']:.2f} ({e['loja_melhor']})")
            total_economia += e['economia_potencial']
        print(f"\n💰 Total que poderia economizar: R$ {total_economia:.2f}")
    else:
        print("\n✅ Ótimo! Preços dentro do esperado.")
    
    return {"economias": economias}

def extrair_itens_cupom(texto_cupom):
    """Extrai itens de um cupom fiscal (OCR ou texto)"""
    # Padrão para identificar linhas de produtos
    import re
    
    itens = []
    lines = texto_cupom.split('\n')
    
    for line in lines:
        # Tenta capturar: código, descrição, qtd, un, vlr_unit, total
        # Ex: 01 7896733401091 IOGURTE HOLANDES 500g N 1 UN 10,97 10,97
        match = re.search(r'(\d+)\s+([\d\.]+)?\s+(.+?)\s+(\d[\d\.,]*)\s+(UN|KG|g|ml|L)?\s+([\d,]+)\s+([\d,]+)', line)
        if match:
            try:
                qtd_str = match.group(4).replace(',', '.')
                if '.' in qtd_str and float(qtd_str) < 10:  # É peso
                    qtd = float(qtd_str)
                    unidade = 'KG' if match.group(5) in ['KG', 'g', 'ml', 'L'] else 'UN'
                else:
                    qtd = int(float(qtd_str))
                    unidade = match.group(5) or 'UN'
                
                vlr_unit = float(match.group(6).replace(',', '.'))
                total = float(match.group(7).replace(',', '.'))
                
                itens.append({
                    'codigo': match.group(2) or '',
                    'nome': match.group(3).strip(),
                    'qtd': qtd,
                    'unidade': unidade,
                    'unitario': vlr_unit,
                    'total': total
                })
            except:
                continue
    
    return itens

def gerar_relatorio_mensal():
    """Gera relatório mensal de gastos"""
    db = load_data("compras")
    
    if not db["compras"]:
        print("❌ Nenhuma compra registrada.")
        return
    
    # Agrupa por mês
    meses = {}
    for compra in db["compras"]:
        mes = compra['data'][:7]  # YYYY-MM
        if mes not in meses:
            meses[mes] = {"total": 0, "compras": 0, "itens": 0}
        meses[mes]["total"] += compra["total"]
        meses[mes]["compras"] += 1
        meses[mes]["itens"] += compra["qtd_itens"]
    
    print("\n" + "="*60)
    print("📊 RELATÓRIO MENSAL DE GASTOS")
    print("="*60)
    
    for mes in sorted(meses.keys(), reverse=True):
        dados = meses[mes]
        print(f"\n{mes}:")
        print(f"  Total gasto: R$ {dados['total']:.2f}")
        print(f"  Compras: {dados['compras']} | Itens: {dados['itens']}")
        print(f"  Média por compra: R$ {dados['total']/dados['compras']:.2f}")

# Inicializa o sistema
if __name__ == "__main__":
    init_system()
    print("\n🛒 Sistema de Controle de Supermercado")
    print("Comandos:")
    print("  - registrar_compra(itens, loja)")
    print("  - analisar_compra(compra)")
    print("  - gerar_relatorio_mensal()")
    print("  - extrair_itens_cupom(texto)")
