
import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import os

# Configuração da página
st.set_page_config(page_title="Controle de Supermercado", page_icon="🛒", layout="wide")

# Caminhos
DATA_DIR = Path("/tmp/supermercado_data")
DB_FILE = DATA_DIR / "compras.json"
PRODUTOS_FILE = DATA_DIR / "produtos.json"

def init_system():
    """Inicializa o sistema"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    if not DB_FILE.exists():
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump({"compras": []}, f, indent=2, ensure_ascii=False)
    
    if not PRODUTOS_FILE.exists():
        with open(PRODUTOS_FILE, 'w', encoding='utf-8') as f:
            json.dump({"produtos": {}}, f, indent=2, ensure_ascii=False)

def load_data(file_type="compras"):
    """Carrega dados"""
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
    """Salva dados"""
    try:
        if file_type == "compras":
            with open(DB_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            with open(PRODUTOS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False

def registrar_compra(itens, loja="DESCONHECIDO"):
    """Registra nova compra"""
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
    
    # Atualiza histórico
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
        
        preco_unit = item['unitario']
        if (produtos_db["produtos"][nome]["melhor_preco"] is None or 
            preco_unit < produtos_db["produtos"][nome]["melhor_preco"]):
            produtos_db["produtos"][nome]["melhor_preco"] = preco_unit
            produtos_db["produtos"][nome]["loja_melhor_preco"] = loja
    
    save_data(db, "compras")
    save_data(produtos_db, "produtos")
    
    return compra

# Inicializa
init_system()

# Título
st.title("🛒 Controle de Supermercado")
st.markdown("Sistema inteligente de controle de gastos e comparação de preços")

# Menu lateral
st.sidebar.title("Menu")
opcao = st.sidebar.radio(
    "Escolha uma opção:",
    ["📝 Nova Compra", "📊 Histórico", "🔍 Consultar Produto", "📈 Relatórios"]
)

if opcao == "📝 Nova Compra":
    st.header("Nova Compra")
    
    loja = st.text_input("Nome da Loja", "BISTEK").upper()
    
    st.subheader("Adicionar Itens")
    
    # Inicializa estado dos itens
    if 'itens_compra' not in st.session_state:
        st.session_state.itens_compra = []
    
    # Formulário para novo item
    with st.form("item_form"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            nome = st.text_input("Produto", "")
        with col2:
            qtd = st.number_input("Qtd", min_value=0.001, value=1.0, step=0.001)
        with col3:
            unitario = st.number_input("Preço Unit. (R$)", min_value=0.01, value=0.00, step=0.01)
        with col4:
            unidade = st.selectbox("Unid.", ["UN", "KG", "G", "ML", "L"])
        
        submitted = st.form_submit_button("➕ Adicionar Item")
        
        if submitted and nome:
            st.session_state.itens_compra.append({
                'nome': nome,
                'qtd': qtd,
                'unitario': unitario,
                'total': qtd * unitario,
                'unidade': unidade
            })
            st.success(f"{nome} adicionado!")
    
    # Mostra itens adicionados
    if st.session_state.itens_compra:
        st.subheader("Itens na Compra")
        for i, item in enumerate(st.session_state.itens_compra):
            st.write(f"{i+1}. **{item['nome']}** x{item['qtd']} = R$ {item['total']:.2f}")
        
        total = sum(item['total'] for item in st.session_state.itens_compra)
        st.metric("Total", f"R$ {total:.2f}")
        
        if st.button("✅ Finalizar Compra"):
            compra = registrar_compra(st.session_state.itens_compra, loja)
            st.success(f"Compra registrada! Total: R$ {compra['total']:.2f}")
            st.session_state.itens_compra = []
            st.rerun()
    
    # Botão limpar
    if st.session_state.itens_compra:
        if st.button("🗑️ Limpar Itens"):
            st.session_state.itens_compra = []
            st.rerun()

elif opcao == "📊 Histórico":
    st.header("Histórico de Compras")
    db = load_data("compras")
    
    if db["compras"]:
        for compra in reversed(db["compras"][-10:]):  # Últimas 10
            with st.expander(f"{compra['data'][:10]} - {compra['loja']} (R$ {compra['total']:.2f})"):
                st.write(f"**Itens:** {compra['qtd_itens']}")
                for item in compra['itens']:
                    st.write(f"- {item['nome']} x{item['qtd']} = R$ {item['total']:.2f}")
    else:
        st.info("Nenhuma compra registrada ainda.")

elif opcao == "🔍 Consultar Produto":
    st.header("Consultar Histórico por Produto")
    
    produtos_db = load_data("produtos")
    
    if produtos_db["produtos"]:
        produto_nome = st.text_input("Nome do produto", "").lower()
        
        if produto_nome and produto_nome in produtos_db["produtos"]:
            hist = produtos_db["produtos"][produto_nome]
            st.subheader(produto_nome.title())
            
            if hist['melhor_preco']:
                st.metric("Melhor Preço", f"R$ {hist['melhor_preco']:.2f}")
                st.write(f"Loja: {hist.get('loja_melhor_preco', 'N/A')}")
            
            if hist['historico']:
                st.write("**Últimas compras:**")
                for reg in hist['historico'][-5:]:
                    st.write(f"- {reg['data'][:10]} | R$ {reg['preco_unit']:.2f} | {reg['loja']}")
        elif produto_nome:
            st.warning("Produto não encontrado.")
    else:
        st.info("Nenhum produto registrado.")

elif opcao == "📈 Relatórios":
    st.header("Relatórios")
    
    db = load_data("compras")
    
    if db["compras"]:
        # Agrupa por mês
        meses = {}
        for compra in db["compras"]:
            mes = compra['data'][:7]
            if mes not in meses:
                meses[mes] = {"total": 0, "compras": 0, "itens": 0}
            meses[mes]["total"] += compra["total"]
            meses[mes]["compras"] += 1
            meses[mes]["itens"] += compra["qtd_itens"]
        
        st.subheader("Gastos Mensais")
        for mes in sorted(meses.keys(), reverse=True):
            dados = meses[mes]
            st.write(f"**{mes}**:")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total", f"R$ {dados['total']:.2f}")
            with col2:
                st.metric("Compras", dados["compras"])
            with col3:
                st.metric("Média", f"R$ {dados['total']/dados['compras']:.2f}")
    else:
        st.info("Nenhuma compra registrada.")
