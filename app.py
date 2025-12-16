import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import kagglehub
import os

st.set_page_config(
    page_title="Dashboard Mercado Olist",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 100% !important;
    }
    
    [data-testid="stVerticalBlock"] {
        gap: 0.5rem;
    }
    
    .stMultiSelect, .stSegmentedControl, .stPills, .stSelectbox {
        width: 100% !important;
    }
    
    [data-testid="column"] {
        padding: 0rem 0.5rem;
    }
    
    h1 {
        padding-top: 0rem;
        margin-bottom: 0.5rem;
    }
    
    .stMarkdown {
        margin-bottom: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title('🛒 Dashboard das Análises do Mercado Olist')

caminho = kagglehub.dataset_download("olistbr/brazilian-ecommerce")
arquivos = sorted(os.listdir(caminho))
clientes = pd.read_csv(os.path.join(caminho, arquivos[0]))
itens = pd.read_csv(os.path.join(caminho, arquivos[2]))
pagamentos = pd.read_csv(os.path.join(caminho, arquivos[3]))
reviews = pd.read_csv(os.path.join(caminho, arquivos[4]))
pedidos = pd.read_csv(os.path.join(caminho, arquivos[5]))
produtos = pd.read_csv(os.path.join(caminho, arquivos[6]))
categorias = pd.read_csv(os.path.join(caminho, arquivos[8]))

tabela_final = (
    clientes
    .merge(pedidos, on='customer_id', how='left')
    .merge(itens, on='order_id', how='left')
    .merge(produtos, on='product_id', how='left')
    .merge(pagamentos, on='order_id', how='left')
    .merge(reviews, on='order_id', how='left')
)
tabela_final = tabela_final[[
    'customer_unique_id',
    'order_id',
    'product_category_name',
    'price',
    'freight_value',
    'payment_type',
    'payment_installments',
    'payment_value',
    'order_status',
    'review_score'
]]

tabela_final = tabela_final[
    (tabela_final['payment_type'].notna()) & 
    (tabela_final['payment_type'] != 'not_defined') &
    (tabela_final['review_score'].notna())
]

st.markdown("---")
st.subheader("🔍 Filtros de Análise")

with st.container():
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        checkbox_cat = st.checkbox("📦 Categoria do Produto", value=False, disabled=False, key='cb_cat')
        if checkbox_cat:
            tipos = sorted(tabela_final['product_category_name'].dropna().unique())
            categorias_selecionadas = st.multiselect(
                'Selecione uma ou mais categorias:',
                tipos,
                key='select_categoria_multiple'
            )
        else:
            categorias_selecionadas = []
    
    with col2:
        checkbox_pag = st.checkbox("💳 Tipos de Pagamento", value=False, disabled=False, key='cb_pag')
        if checkbox_pag:
            pagamentos = sorted(tabela_final['payment_type'].dropna().unique())
            pagamento_selecionado = st.segmented_control(
                'Selecione o tipo:',
                pagamentos,
                key='select_pagamento'
            )
        else:
            pagamento_selecionado = None
    
    with col3:
        checkbox_rev = st.checkbox("⭐ Reviews", value=False, disabled=False, key='cb_rev')
        if checkbox_rev:
            reviews = sorted(tabela_final['review_score'].unique())
            reviews_selecionadas = st.multiselect(
                'Selecione uma ou mais notas:',
                reviews,
                key='select_review_multiple'
            )
        else:
            reviews_selecionadas = []

st.markdown("---")

aba_tabela, aba_visualizacao = st.tabs(["📋 Tabela de Dados", "📈 Visualizações"])

with aba_tabela:
    df_tabela = tabela_final.copy()
    if categorias_selecionadas:
        df_tabela = df_tabela[df_tabela['product_category_name'].isin(categorias_selecionadas)]
    
    if pagamento_selecionado:
        df_tabela = df_tabela[df_tabela['payment_type'] == pagamento_selecionado]
    
    if reviews_selecionadas:
        df_tabela = df_tabela[df_tabela['review_score'].isin(reviews_selecionadas)]
    
    if not df_tabela.empty:
        st.write(f"**Total de registros filtrados:** {len(df_tabela):,}")
        
        st.dataframe(
            df_tabela,
            use_container_width=True,
            height=400
        )
        
        @st.cache_data
        def converter_df_para_csv(df):
            return df.to_csv(index=False).encode('utf-8')
        
        csv_tabela = converter_df_para_csv(df_tabela)
        
        nome_arquivo = f"dados_filtrados_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        st.download_button(
            label="📥 **Baixar Tabela como CSV**",
            data=csv_tabela,
            file_name=nome_arquivo,
            mime="text/csv",
            key='download_tabela_filtrada'
        )
        
    else:
        st.info("Nenhum dado encontrado com os filtros selecionados.")

with aba_visualizacao:
    filtrado = tabela_final.copy()
    
    if categorias_selecionadas:
        filtrado = filtrado[filtrado['product_category_name'].isin(categorias_selecionadas)]
    
    if pagamento_selecionado:
        filtrado = filtrado[filtrado['payment_type'] == pagamento_selecionado]
    
    if reviews_selecionadas:
        filtrado = filtrado[filtrado['review_score'].isin(reviews_selecionadas)]
    
    if filtrado.empty:
        st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
        st.stop()
    
    if not (checkbox_cat or checkbox_pag or checkbox_rev):
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            total_pedidos = len(filtrado['order_id'].unique())
            st.metric("Total de Pedidos", f"{total_pedidos:,}")
        
        with metric_col2:
            total_clientes = len(filtrado['customer_unique_id'].unique())
            st.metric("Total de Clientes", f"{total_clientes:,}")
        
        with metric_col3:
            categorias_unicas = len(filtrado['product_category_name'].unique())
            st.metric("Categorias Únicas", f"{categorias_unicas:,}")
        
        with metric_col4:
            media_review = filtrado['review_score'].mean()
            st.metric("Média de Avaliações", f"{media_review:.2f}")
    
    elif checkbox_cat and not checkbox_pag and not checkbox_rev:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            total_pedidos_cat = len(filtrado['order_id'].unique())
            st.metric("Total de Pedidos", f"{total_pedidos_cat:,}")
        
        with col2:
            media_valor_produto = filtrado['price'].mean()
            st.metric("Valor Médio Produto", f"R${media_valor_produto:.2f}")
        
        with col3:
            pagamento_mais_usado = filtrado['payment_type'].value_counts().index[0]
            traducao_pagamento = {
                'boleto': 'Boleto',
                'credit_card': 'Credito',
                'debit_card': 'Debito',
                'voucher': 'Voucher'
            }
            pagamento_traduzido = traducao_pagamento.get(pagamento_mais_usado, pagamento_mais_usado)
            st.metric("Pagamento Mais Usado", pagamento_traduzido)
        
        with col4:
            media_avaliacoes = filtrado['review_score'].mean()
            st.metric("Média Avaliações", f"{media_avaliacoes:.2f}")
        
    elif checkbox_pag and not checkbox_cat and not checkbox_rev:
        col1, col2, col3, col4 = st.columns([1, 1, 1.5, 1])
        
        with col1:
            total_pagamentos = len(filtrado)
            st.metric("Total de Pagamentos", f"{total_pagamentos:,}")
        
        with col2:
            media_valor_pagamento = filtrado['payment_value'].mean()
            st.metric("Valor Médio", f"R${media_valor_pagamento:.2f}")
        
        with col3:
            categoria_mais_pagou = filtrado['product_category_name'].value_counts().index[0]
            st.metric("Categoria Mais Frequente", categoria_mais_pagou)
        
        with col4:
            media_avaliacoes_pag = filtrado['review_score'].mean()
            st.metric("Média Avaliações", f"{media_avaliacoes_pag:.2f}")

    elif checkbox_rev and not checkbox_cat and not checkbox_pag:
        col1, col2, col3 = st.columns([1, 1.5, 1])
        
        with col1:
            total_avaliacoes = len(filtrado)
            st.metric("Total de Avaliações", f"{total_avaliacoes:,}")
        
        with col2:
            categoria_mais_avaliada = filtrado['product_category_name'].value_counts().index[0]
            st.metric("Categoria Mais Avaliada", categoria_mais_avaliada)
        
        with col3:
            valor_medio_review = filtrado['price'].mean()
            st.metric("Valor Médio Produto", f"R${valor_medio_review:.2f}")

    elif checkbox_cat and checkbox_pag and not checkbox_rev:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_pedidos_combinado = len(filtrado['order_id'].unique())
            st.metric("Total de Pedidos", f"{total_pedidos_combinado:,}")
        
        with col2:
            media_valor_combinado = filtrado['price'].mean()
            st.metric("Valor Médio Produto", f"R${media_valor_combinado:.2f}")
        
        with col3:
            media_review_combinado = filtrado['review_score'].mean()
            st.metric("Média das Reviews", f"{media_review_combinado:.2f}")

    elif checkbox_cat and checkbox_rev and not checkbox_pag:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_pedidos_cat_rev = len(filtrado['order_id'].unique())
            st.metric("Total de Pedidos", f"{total_pedidos_cat_rev:,}")
        
        with col2:
            media_valor_cat_rev = filtrado['price'].mean()
            st.metric("Valor Médio Produto", f"R${media_valor_cat_rev:.2f}")
        
        with col3:
            pagamento_mais_comum = filtrado['payment_type'].value_counts().index[0]
            traducao_pagamento = {
                'boleto': 'Boleto',
                'credit_card': 'Credito',
                'debit_card': 'Debito',
                'voucher': 'Voucher'
            }
            pagamento_traduzido = traducao_pagamento.get(pagamento_mais_comum, pagamento_mais_comum)
            st.metric("Pagamento Mais Usado", pagamento_traduzido)

    elif checkbox_pag and checkbox_rev and not checkbox_cat:
        col1, col2, col3 = st.columns([1, 1, 1.5])
        
        with col1:
            total_pedidos_pag_rev = len(filtrado['order_id'].unique())
            st.metric("Total de Pedidos", f"{total_pedidos_pag_rev:,}")
        
        with col2:
            media_valor_pag_rev = filtrado['price'].mean()
            st.metric("Valor Médio Produto", f"R${media_valor_pag_rev:.2f}")
        
        with col3:
            categoria_mais_comum = filtrado['product_category_name'].value_counts().index[0]
            st.metric("Categoria Mais Comum", categoria_mais_comum)

    elif checkbox_cat and checkbox_pag and checkbox_rev:
        col1, col2 = st.columns(2)
        
        with col1:
            total_pedidos_completo = len(filtrado['order_id'].unique())
            st.metric("Total de Pedidos", f"{total_pedidos_completo:,}")
        
        with col2:
            media_valor_completo = filtrado['price'].mean()
            st.metric("Valor Médio Produto", f"R${media_valor_completo:.2f}")

    st.markdown("---")
    st.subheader("📊 Gráficos")

    with st.container():
        
        if checkbox_cat and not checkbox_pag and not checkbox_rev:
            
            if categorias_selecionadas:
                dados_grafico = filtrado['product_category_name'].value_counts()
            else:
                dados_grafico = tabela_final['product_category_name'].value_counts().head(15)
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            bars = ax.bar(range(len(dados_grafico)), dados_grafico.values, color='#219ebc')
            ax.set_xlabel('Categorias de Produtos', fontsize=12)
            ax.set_ylabel('Quantidade de Vendas', fontsize=12)
            ax.set_title('Distribuição por Categoria de Produto', fontsize=14)
            ax.set_xticks(range(len(dados_grafico)))
            ax.set_xticklabels(dados_grafico.index, rotation=45, ha='right', fontsize=10)
            
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height):,}', ha='center', va='bottom', fontsize=9)
            
            plt.tight_layout()
            st.pyplot(fig)
        
        elif checkbox_pag and not checkbox_cat and not checkbox_rev:
            
            dados_pagamento = tabela_final['payment_type'].value_counts()
            
            traducao_pagamento = {
                'boleto': 'Boleto',
                'credit_card': 'Crédito',
                'debit_card': 'Débito',
                'voucher': 'Voucher'
            }
            labels = [traducao_pagamento.get(x, x) for x in dados_pagamento.index]
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            colors = ['#8ecae6', '#219ebc', '#023047', '#ffb703']
            wedges, texts, autotexts = ax.pie(dados_pagamento.values, labels=labels, autopct='%1.1f%%',
                                            startangle=90, colors=colors)
            ax.axis('equal')
            ax.set_title('Distribuição por Tipo de Pagamento', fontsize=14, pad=20)
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            plt.tight_layout()
            st.pyplot(fig)
        
        elif checkbox_rev and not checkbox_cat and not checkbox_pag:
            
            dados_review = tabela_final['review_score'].value_counts().sort_index()
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            colors = ['#8ecae6', '#219ebc', '#023047', '#ffb703', '#fb8500']
            wedges, texts, autotexts = ax.pie(dados_review.values, labels=[f'Nota {i}' for i in dados_review.index],
                                            autopct='%1.1f%%', startangle=90, colors=colors)
            ax.axis('equal')
            ax.set_title('Distribuição por Nota de Avaliação', fontsize=14, pad=20)
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            plt.tight_layout()
            st.pyplot(fig)
        
        elif checkbox_cat and checkbox_pag and not checkbox_rev:
            
            if categorias_selecionadas:
                dados_grafico = filtrado
            else:
                top_categorias = tabela_final['product_category_name'].value_counts().head(10).index
                dados_grafico = tabela_final[tabela_final['product_category_name'].isin(top_categorias)]
            
            tabela_cruzada = pd.crosstab(dados_grafico['product_category_name'], 
                                        dados_grafico['payment_type'])
            
            tabela_cruzada['total'] = tabela_cruzada.sum(axis=1)
            tabela_cruzada = tabela_cruzada.sort_values('total', ascending=False).drop('total', axis=1)
            
            traducao_pagamento = {
                'boleto': 'Boleto',
                'credit_card': 'Crédito',
                'debit_card': 'Débito',
                'voucher': 'Voucher'
            }
            tabela_cruzada.columns = [traducao_pagamento.get(x, x) for x in tabela_cruzada.columns]
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            bottom = np.zeros(len(tabela_cruzada))
            colors = ['#8ecae6', '#219ebc', '#023047', '#ffb703']
            
            for i, pagamento in enumerate(tabela_cruzada.columns):
                ax.bar(tabela_cruzada.index, tabela_cruzada[pagamento], bottom=bottom, 
                    label=pagamento, color=colors[i % len(colors)], alpha=0.8)
                bottom += tabela_cruzada[pagamento].values
            
            ax.set_xlabel('Categorias de Produtos', fontsize=12)
            ax.set_ylabel('Quantidade', fontsize=12)
            ax.set_title('Distribuição de Pagamentos por Categoria', fontsize=14)
            ax.set_xticks(range(len(tabela_cruzada)))
            ax.set_xticklabels(tabela_cruzada.index, rotation=45, ha='right', fontsize=10)
            ax.legend(title='Tipo de Pagamento', bbox_to_anchor=(1.05, 1), loc='upper left')
            
            plt.tight_layout()
            st.pyplot(fig)
        
        elif checkbox_cat and checkbox_rev and not checkbox_pag:
            
            if categorias_selecionadas:
                dados_cat_rev = filtrado
            else:
                top_categorias = tabela_final['product_category_name'].value_counts().head(5).index
                dados_cat_rev = tabela_final[tabela_final['product_category_name'].isin(top_categorias)]
            
            tabela_cruzada = pd.crosstab(dados_cat_rev['product_category_name'], 
                                        dados_cat_rev['review_score'])
            
            tabela_cruzada['total'] = tabela_cruzada.sum(axis=1)
            tabela_cruzada = tabela_cruzada.sort_values('total', ascending=False).drop('total', axis=1)
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            bottom = np.zeros(len(tabela_cruzada))
            colors = ['#8ecae6', '#219ebc', '#023047', '#ffb703', '#fb8500']
            
            for i, review in enumerate(sorted(tabela_cruzada.columns)):
                ax.bar(tabela_cruzada.index, tabela_cruzada[review], bottom=bottom, 
                    label=f'Nota {review}', color=colors[i % len(colors)], alpha=0.8)
                bottom += tabela_cruzada[review].values
            
            ax.set_xlabel('Categorias de Produtos', fontsize=12)
            ax.set_ylabel('Quantidade', fontsize=12)
            ax.set_title('Distribuição de Avaliações por Categoria', fontsize=14)
            ax.set_xticks(range(len(tabela_cruzada)))
            ax.set_xticklabels(tabela_cruzada.index, rotation=45, ha='right', fontsize=10)
            ax.legend(title='Nota', bbox_to_anchor=(1.05, 1), loc='upper left')
            
            plt.tight_layout()
            st.pyplot(fig)
        
        elif checkbox_pag and checkbox_rev and not checkbox_cat:
            tabela_cruzada = pd.crosstab(tabela_final['payment_type'], 
                                        tabela_final['review_score'])
            
            traducao_pagamento = {
                'boleto': 'Boleto',
                'credit_card': 'Crédito',
                'debit_card': 'Débito',
                'voucher': 'Voucher'
            }
            tabela_cruzada.index = [traducao_pagamento.get(x, x) for x in tabela_cruzada.index]
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            tabela_normalizada = tabela_cruzada.div(tabela_cruzada.sum(axis=1), axis=0)          

            sns.heatmap(tabela_normalizada, annot=True, fmt=".2%", cmap=custom_cmap, 
                       cbar_kws={'label': 'Proporção'}, ax=ax,
                       linewidths=0.5, linecolor='black')
            
            ax.set_xlabel('Nota de Avaliação', fontsize=12)
            ax.set_ylabel('Tipo de Pagamento', fontsize=12)
            ax.set_title('Proporção de Avaliações por Tipo de Pagamento', fontsize=14)
            
            plt.tight_layout()
            st.pyplot(fig)

        elif checkbox_cat and checkbox_pag and checkbox_rev:
 
            st.info("Para visualizar gráficos específicos, selecione apenas 1 ou 2 opções de filtro.")

    if not (checkbox_cat or checkbox_pag or checkbox_rev):
        st.info("Ative pelo menos um filtro para visualizar os gráficos analíticos.")
