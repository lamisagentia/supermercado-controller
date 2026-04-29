# 🛒 Sistema de Controle de Gastos - Supermercado

Desenvolvido por: **Lamis Agent**  
Finalidade: Controlar compras de supermercado, comparar preços e sugerir economia

---

## 📋 Visão Geral

Este sistema permite:
- ✅ Registrar compras de supermercado (via imagem ou manual)
- ✅ Extrair dados de cupons fiscais usando OCR
- ✅ Armazenar histórico de preços por produto
- ✅ Comparar preços entre diferentes lojas
- ✅ Identificar produtos mais caros que o habitual
- ✅ Gerar relatórios mensais de gastos
- ✅ Sugerir onde comprar cada item mais barato

---

## 🚀 Instalação

### 1. Instalar dependências

```bash
# Python packages
pip install pillow pytesseract

# Tesseract OCR (sistema)
apt-get update
apt-get install -y tesseract-ocr tesseract-ocr-por
```

### 2. Estrutura de Arquivos

```
/root/supermercado/
├── sistema.py          # Núcleo do sistema
├── processar_cupom.py  # Processamento de imagens
├── interface.py        # Interface interativa
├── README.md           # Este arquivo
└── dados/              # Armazenamento local
    ├── compras.json    # Histórico de compras
    └── produtos.json   # Histórico de preços
```

---

## 📖 Como Usar

### Modo 1: Interface Interativa

```bash
cd /root/supermercado
python3 interface.py
```

**Menu principal:**
1. 📸 Processar cupom (imagem)
2. ✍️ Lançar compra manualmente
3. 📊 Ver relatório mensal
4. 🔍 Consultar histórico de produto
5. 📈 Top 5 produtos mais comprados

### Modo 2: Processar Imagem de Cupom

```bash
python3 processar_cupom.py /caminho/da/imagem.jpg
```

### Modo 3: Via API/Script

```python
from sistema import registrar_compra, analisar_compra

# Itens da compra
itens = [
    {'nome': 'LEITE UHT 1L', 'qtd': 6, 'unitario': 4.99, 'total': 29.94},
    {'nome': 'PÃO FATIADO', 'qtd': 2, 'unitario': 7.49, 'total': 14.98}
]

# Registrar
compra = registrar_compra(itens, "BISTEK")

# Analisar
analisar_compra(compra)
```

---

## 📊 Funcionalidades

### Registro Automático de Compras
- Extrai dados de cupons fiscais via OCR
- Identifica: produto, quantidade, preço unitário, total, loja
- Armazena data/hora automaticamente

### Comparação de Preços
- Mantém histórico de preços por produto
- Identifica melhor preço já registrado
- Alerta quando produto está mais caro que o habitual (>10%)
- Sugere loja mais barata para cada item

### Relatórios
- Gastos mensais consolidados
- Média por compra
- Top 5 produtos mais comprados
- Evolução de preços ao longo do tempo

---

## 💡 Exemplo de Uso

```bash
# Inicia o sistema
python3 interface.py

# Opção 2: Lançar compra manual
Loja: BISTEK
Produto: LEITE UHT TIROL 1L
Quantidade: 6
Preço unitário: 4.99

# Sistema registra e analisa
✅ Compra registrada!
⚠️ Produto 15% mais caro que média
💰 Economia potencial: R$ 4,50
```

---

## 🔧 Personalização

### Adicionar Novas Loias
Basta informar o nome da loja ao registrar a compra. O sistema aprende automaticamente.

### Ajustar Limite de Alerta
No arquivo `sistema.py`, altere:
```python
if melhor and atual > melhor * 1.1:  # 10% atualmente
```

### Exportar Dados
Os dados estão em JSON em:
- `/root/.hermes/supermercado/compras.json`
- `/root/.hermes/supermercado/produtos.json`

---

## 🎯 Próximos Passos (Sugestões)

1. **Integração Telegram**: Enviar foto do cupom e receber análise
2. **OCR Aprimorado**: Treinar modelo específico para cupons brasileiros
3. **Exportação Excel**: Gerar planilhas para análise avançada
4. **Meta Orçamento**: Alertar quando ultrapassar teto mensal
5. **Receitas x Preço**: Sugerir receitas baseadas em promoções

---

## 📞 Suporte

Desenvolvido por **Lamis Agent**  
Para dúvidas ou melhorias, solicite ajustes!

---

## 📝 Licença

Uso pessoal e gratuito.
