import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Análise de Preços", layout="wide")

# Função para carregar dados
def load_data(uploaded_file):
    if uploaded_file.name.endswith('.xlsx'):
        return pd.read_excel(uploaded_file)
    else:
        return pd.read_csv(uploaded_file)

# Interface principal
st.title('📊 Sistema de Análise de Preços')
st.markdown("""
Faça upload da planilha do fornecedor e analise os preços dos produtos.
""")

# Upload do arquivo
uploaded_file = st.file_uploader("Selecione o arquivo (XLSX ou CSV)", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        df = load_data(uploaded_file)
        st.session_state['df'] = df
        
        # Pré-visualização
        st.subheader("Visualização dos Dados")
        st.dataframe(df.head(), use_container_width=True)
        
        # Estatísticas rápidas
        st.subheader("📈 Estatísticas Básicas")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Produtos", len(df))
        
        with col2:
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                col_preco = st.selectbox("Coluna de preço", options=numeric_cols)
                st.metric("Preço Médio", f"R$ {df[col_preco].mean():.2f}")
        
        with col3:
            if len(numeric_cols) > 0:
                st.metric("Preço Máximo", f"R$ {df[col_preco].max():.2f}")
        
        # Busca de produtos
        st.subheader("🔍 Busca de Produtos")
        search_col, search_term = st.columns(2)
        
        with search_col:
            coluna_busca = st.selectbox("Coluna para busca", options=df.columns)
        
        with search_term:
            termo_busca = st.text_input("Termo de busca")
        
        if termo_busca:
            resultado = df[df[coluna_busca].astype(str).str.contains(termo_busca, case=False, na=False)]
            
            if not resultado.empty:
                st.success(f"Encontrados {len(resultado)} produtos")
                st.dataframe(resultado, use_container_width=True)
                
                # Análise detalhada
                st.subheader("📌 Análise Detalhada")
                selected_product = st.selectbox(
                    "Selecione um produto para análise",
                    options=resultado[coluna_busca].unique()
                )
                
                product_data = resultado[resultado[coluna_busca] == selected_product]
                st.write(product_data)
                
                # Visualização
                if len(numeric_cols) > 0:
                    fig, ax = plt.subplots()
                    ax.hist(df[col_preco], bins=20, alpha=0.5)
                    ax.axvline(x=product_data[col_preco].values[0], color='r', linestyle='--')
                    ax.set_title('Distribuição de Preços')
                    ax.set_xlabel('Preço')
                    ax.set_ylabel('Frequência')
                    st.pyplot(fig)
                    
                    # Comparação
                    price_diff = product_data[col_preco].values[0] - df[col_preco].mean()
                    st.metric(
                        label="Diferença para a média", 
                        value=f"R$ {price_diff:.2f}",
                        delta=f"{price_diff/df[col_preco].mean()*100:.1f}%"
                    )
            else:
                st.warning("Nenhum produto encontrado com esse termo de busca.")
        
        # Análise adicional
        st.subheader("📊 Análise Avançada")
        if len(numeric_cols) > 0:
            tab1, tab2 = st.tabs(["Distribuição", "Top Produtos"])
            
            with tab1:
                st.bar_chart(df[col_preco].value_counts(bins=10))
            
            with tab2:
                top_n = st.slider("Número de produtos", 5, 50, 10)
                top_products = df.nlargest(top_n, col_preco)[[coluna_busca, col_preco]]
                st.dataframe(top_products, use_container_width=True)
    
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {str(e)}")

# Rodapé
st.markdown("---")
st.caption("Sistema de análise de preços v1.0 | Desenvolvido com Streamlit")
