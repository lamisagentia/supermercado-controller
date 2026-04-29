#!/usr/bin/env python3
"""
Processador de Cupons Fiscais - Supermercado
Extrai dados de imagens de cupons usando OCR
"""

import sys
import os
sys.path.insert(0, '/root/supermercado')

from sistema import registrar_compra, analisar_compra, init_system
import re

def processar_cupum_bistek():
    """
    Exemplo de processamento do cupom Bistek
    Este será substituído por OCR real quando receber a imagem
    """
    
    # Dados extraídos do cupom Bistek (exemplo real)
    itens_cupom = [
        {'nome': 'IOGURTE HOLANDES 500g', 'qtd': 1, 'unitario': 10.97, 'total': 10.97, 'unidade': 'UN'},
        {'nome': 'LEITE UHT TIROL 1L', 'qtd': 6, 'unitario': 4.99, 'total': 29.94, 'unidade': 'UN'},
        {'nome': 'PCT BATATA PALHA 100g', 'qtd': 2, 'unitario': 8.49, 'total': 16.98, 'unidade': 'UN'},
        {'nome': 'BISCOITO RECHEADO 140g', 'qtd': 3, 'unitario': 3.99, 'total': 11.97, 'unidade': 'UN'},
        {'nome': 'REFRIGERANTE 2L', 'qtd': 2, 'unitario': 9.99, 'total': 19.98, 'unidade': 'UN'},
        {'nome': 'SABAO EM PO 1KG', 'qtd': 1, 'unitario': 15.90, 'total': 15.90, 'unidade': 'UN'},
        {'nome': 'PAO FATIADO 500g', 'qtd': 2, 'unitario': 7.49, 'total': 14.98, 'unidade': 'UN'},
        {'nome': 'QUEIJO MUSSARELA KG', 'qtd': 0.356, 'unitario': 59.90, 'total': 21.32, 'unidade': 'KG'},
    ]
    
    print("\\n📝 Processando cupom fiscal...")
    print(f"Loja: BISTEK SUPERMERCADOS")
    print(f"Total de itens: {len(itens_cupom)}")
    
    # Registra a compra
    compra = registrar_compra(itens_cupom, "BISTEK")
    
    print(f"\\n✅ Compra registrada com sucesso!")
    print(f"ID: {compra['id']}")
    print(f"Total: R$ {compra['total']:.2f}")
    
    # Analisa a compra
    analisar_compra(compra)
    
    return compra

def extrair_texto_imagem(caminho_imagem):
    """
    Extrai texto de imagem usando OCR
    Requer: tesseract-ocr instalado
    """
    try:
        import pytesseract
        from PIL import Image
        
        # Carrega imagem
        img = Image.open(caminho_imagem)
        
        # Extrai texto com OCR
        texto = pytesseract.image_to_string(img, lang='por')
        
        return texto
    except ImportError:
        print("⚠️  pytesseract não instalado. Instale com: pip install pytesseract pillow")
        return None
    except Exception as e:
        print(f"❌ Erro ao processar imagem: {e}")
        return None

def parsear_itens_texto(texto):
    """
    Converte texto OCR em lista de itens
    """
    itens = []
    lines = texto.split('\\n')
    
    for line in lines:
        # Padrão simplificado para cupons brasileiros
        # Procura linhas com preço (R$ ou valores com vírgula)
        if re.search(r'\\d+[,.]\\d{2}', line):
            # Tenta extrair: descrição e preço
            match = re.search(r'([A-ZÀ-Ü][A-Za-zÀ-ü0-9\\s\\.]+)\\s+([\\d]+)[,.]([\\d]{2})', line)
            if match:
                try:
                    nome = match.group(1).strip()
                    preco_str = f"{match.group(2)}.{match.group(3)}"
                    preco = float(preco_str)
                    
                    itens.append({
                        'nome': nome,
                        'qtd': 1,
                        'unitario': preco,
                        'total': preco,
                        'unidade': 'UN'
                    })
                except:
                    continue
    
    return itens

if __name__ == "__main__":
    init_system()
    
    if len(sys.argv) > 1:
        # Processa imagem fornecida
        caminho = sys.argv[1]
        print(f"\\n📷 Processando imagem: {caminho}")
        
        texto = extrair_texto_imagem(caminho)
        if texto:
            itens = parsear_itens_texto(texto)
            if itens:
                compra = registrar_compra(itens, "AUTO")
                analisar_compra(compra)
            else:
                print("❌ Nenhum item encontrado na imagem.")
        else:
            print("❌ Falha ao extrair texto da imagem.")
    else:
        # Modo demonstração
        print("\\n🛒 Processador de Cupons - Modo Demonstração")
        processar_cupum_bistek()
