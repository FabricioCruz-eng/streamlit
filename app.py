import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Consulta dos Dados 📚", layout="wide")

# Função para carregar dados do Excel
@st.cache_data
def load_data(file):
    try:
        df = pd.read_excel(file)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
        return None

# Barra lateral com filtros
with st.sidebar:
    st.header("Filtros 🔎")
    ano_selecionado = st.selectbox("Selecione o ano", options=[2024, 2025])
    
    # A operadora será preenchida dinamicamente se um arquivo for carregado
    #operadora_selecionada = st.selectbox("Operadora", options=["Todas"])
    
    localidade_selecionada = st.selectbox("Selecione a localidade", options=[
        'AC','AM', 'AL', 'AP', 'BA', 'CE','ES','GO' ,'MA','MG','MS','MT',
        'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 'RO','RR', 'RS','SC','SE','SP', 'TO'
    ])

# Título do aplicativo
st.title("Ferramenta de Pesquisa de Dados 📈")

# Upload do arquivo Excel
uploaded_file = st.file_uploader("Carregar arquivo Excel", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Carregar dados
    df = load_data(uploaded_file)
    
    if df is not None:
        # Atualizar opções de operadora na barra lateral
        if 'Operadora' in df.columns:
            with st.sidebar:
                operadoras = ["Todas"] + sorted(df['Operadora'].unique().tolist())
                operadora_selecionada = st.selectbox("Operadora", options=operadoras, key='operadora_dynamic')
        
        # Filtrar dados com base nas seleções da barra lateral
        df_filtrado = df.copy()
        
        # Aplicar filtro de operadora se não for "Todas"
        if 'Operadora' in df.columns and operadora_selecionada != "Todas":
            df_filtrado = df_filtrado[df_filtrado['Operadora'] == operadora_selecionada]

                       
        # Mostrar estatísticas básicas
        st.subheader("Visão Geral dos Dados")
        st.subheader("Estastíticas Descritivas")
        st.write(f"Total de registros: {len(df_filtrado)}")
        
        # Exibir os dados
        with st.expander("Visualizar todos os dados"):
            st.dataframe(df_filtrado)
        
        # Seção de pesquisa
        st.subheader("Pesquisar Dados")
        
        # Selecionar colunas para pesquisa
        col1, col2 = st.columns(2)
        
        with col1:
            search_columns = st.multiselect(
                "Selecione as colunas para pesquisa:",
                options=df_filtrado.columns.tolist(),
                default=df_filtrado.columns[0:3].tolist()
            )
        
        with col2:
            search_term = st.text_input("Digite o termo de pesquisa:")
        
        # Botão de pesquisa
        if st.button("Pesquisar"):
            if search_term and search_columns:
                filtered_df = pd.DataFrame()
                
                for column in search_columns:
                    # Converter para string para garantir que a pesquisa funcione em todos os tipos de dados
                    temp_df = df_filtrado[df_filtrado[column].astype(str).str.contains(search_term, case=False, na=False)]
                    filtered_df = pd.concat([filtered_df, temp_df]).drop_duplicates()
                
                if not filtered_df.empty:
                    st.success(f"Encontrados {len(filtered_df)} resultados.")
                    st.dataframe(filtered_df)
                    
                    # Opção para download dos resultados
                    csv = filtered_df.to_csv(index=False)
                    st.download_button(
                        label="Baixar resultados como CSV",
                        data=csv,
                        file_name="resultados_pesquisa.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning(f"Nenhum resultado encontrado para '{search_term}' nas colunas selecionadas.")
            else:
                st.warning("Por favor, selecione pelo menos uma coluna e digite um termo para pesquisa.")
        
        # Filtros avançados
        st.subheader("Filtros Avançados")
        
        # Selecionar coluna para filtro
        filter_column = st.selectbox("Selecione uma coluna para filtrar:", options=df_filtrado.columns.tolist())
        
        # Obter valores únicos da coluna selecionada
        unique_values = df_filtrado[filter_column].dropna().unique().tolist()
        
        # Filtrar por valores específicos
        selected_values = st.multiselect(
            f"Filtrar {filter_column} por valores específicos:",
            options=unique_values
        )
        
        if selected_values:
            filtered_df = df_filtrado[df_filtrado[filter_column].isin(selected_values)]
            st.dataframe(filtered_df)
            
            # Opção para download dos resultados filtrados
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Baixar resultados filtrados como CSV",
                data=csv,
                file_name="resultados_filtrados.csv",
                mime="text/csv"
            )
        
        # Visualizações
        st.subheader("Visualizações")
        
        # Selecionar colunas para visualização
        viz_col1, viz_col2 = st.columns(2)
        
        with viz_col1:
            chart_type = st.selectbox(
                "Tipo de gráfico:",
                options=["Barras", "Linhas", "Dispersão", "Pizza"]
            )
        
        with viz_col2:
            numeric_columns = df_filtrado.select_dtypes(include=["int64", "float64"]).columns.tolist()
            if numeric_columns:
                y_column = st.selectbox("Selecione a coluna para o eixo Y:", options=numeric_columns)
                
                # Apenas para gráficos que precisam de uma coluna categórica para o eixo X
                if chart_type in ["Barras", "Linhas"]:
                    categorical_columns = df_filtrado.select_dtypes(exclude=["int64", "float64"]).columns.tolist()
                    x_column = st.selectbox("Selecione a coluna para o eixo X:", options=categorical_columns if categorical_columns else df_filtrado.columns.tolist())
                elif chart_type == "Dispersão":
                    x_column = st.selectbox("Selecione a coluna para o eixo X:", options=numeric_columns)
                elif chart_type == "Pizza":
                    categorical_columns = df_filtrado.select_dtypes(exclude=["int64", "float64"]).columns.tolist()
                    x_column = st.selectbox("Selecione a coluna de categorias:", options=categorical_columns if categorical_columns else df_filtrado.columns.tolist())
                
                # Criar gráfico
                if st.button("Gerar Gráfico"):
                    st.subheader(f"Gráfico de {chart_type}")
                    
                    if chart_type == "Barras":
                        fig = px.bar(df_filtrado, x=x_column, y=y_column, title=f"{y_column} por {x_column}")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif chart_type == "Linhas":
                        fig = px.line(df_filtrado, x=x_column, y=y_column, title=f"{y_column} por {x_column}")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif chart_type == "Dispersão":
                        fig = px.scatter(df_filtrado, x=x_column, y=y_column, title=f"{y_column} vs {x_column}")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif chart_type == "Pizza":
                        # Agrupar dados para gráfico de pizza
                        pie_data = df_filtrado.groupby(x_column)[y_column].sum().reset_index()
                        fig = px.pie(pie_data, values=y_column, names=x_column, title=f"Distribuição de {y_column} por {x_column}")
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Não foram encontradas colunas numéricas para visualização.")
else:
    st.info("Por favor, carregue um arquivo Excel para começar.")
    
    # Exemplo de como os dados devem estar formatados
    st.subheader("Formato esperado dos dados:")
    exemplo = {
        "Km": [80.3, 127.6, 26, 238.3, 208.9],
        "Operadora": ["OMEGA NET", "ALFA TELECOM", "ALFA TELECOM", "BETA FIBRA", "OMEGA NET"],
        "Rota": ["CIDADE 6 - CIDADE 1", "CIDADE 1 - CIDADE 2", "CIDADE 2 - CIDADE 3", "CIDADE 3 - CIDADE 4", "CIDADE 4 - CIDADE 5"],
        "Instalacao": ["RODOVIÁRIO (ENTERRADO)", "RODOVIÁRIO (AÉREO)", "RODOVIÁRIO (AÉREO)", "FERROVIÁRIO", "FERROVIÁRIO"],
        "Jan": [0, 0, 0, 1, 0],
        "Fev": [0, 0, 0, 0, 1]
    }
    st.dataframe(pd.DataFrame(exemplo)) 


st.markdown("""---""")
st.markdown("""
🔥 Ainda precisa de mais informações? Acesse o portal - http://sit.nocclarobrasil.com.br/Roma/Default.aspx         

Ferramenta criada e mantida por fabricio.cruz@claro.com.br
            
### Dados Utilizados
Os arquivos utilizados na análise estão disponíveis em:
1. Repositório de Dados do Portal Roma ./xls
2. Disponibilidade ./trecho""")



                                                                                               st.markdown(""" Todos os direitos reservados. Política de Privacidade - Termos de Uso 
                                                                                                                       Claro Brasil""")
