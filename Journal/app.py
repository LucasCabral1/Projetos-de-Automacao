import streamlit as st
import sqlite3
import pandas as pd

DB_NAME = "my_journal.db"

@st.cache_data 
def load_data():
    try:
        conn = sqlite3.connect(DB_NAME)
        
        query = """
            SELECT 
                title AS "Título", 
                url AS "URL", 
                source_name AS "Fonte", 
                topic AS "Tópico", 
                published_at, 
                ID,
                generic_news 
            FROM articles 
            ORDER BY published_at DESC
        """
        # ---------------------
        
        df = pd.read_sql_query(query, conn)
        return df
    except sqlite3.Error as e:
        st.error(f"Ocorreu um erro ao ler o banco de dados: {e}")
        return pd.DataFrame(columns=["Título", "URL", "Fonte", "Tópico", "published_at", "ID", "generic_news"])
    finally:
        if 'conn' in locals() and conn:
            conn.close()

st.set_page_config(page_title="MyJournal", layout="wide")
st.title("MyJournal - Arquivo de Notícias 📰")

df = load_data()

if df.empty:
    st.warning("O banco de dados está vazio. Execute o script principal de coleta de notícias primeiro.")
else:
    st.sidebar.header("Filtros")
    
    all_topics = df['Tópico'].unique()
    selected_topics = st.sidebar.multiselect("Filtrar por Tópico:", options=all_topics, default=all_topics)

    all_sources = df['Fonte'].unique()
    selected_sources = st.sidebar.multiselect("Filtrar por Fonte:", options=all_sources, default=all_sources)

    search_title = st.sidebar.text_input("Buscar no Título:")
    
    df_specific = df[df['generic_news'] == 0] 
    
    df_generic = df[df['generic_news'] == 1]
    
    tab_specific, tab_generic = st.tabs(["Notícias Específicas (RSS)", "Notícias Gerais (Tópicos)"])

    with tab_specific:
        st.header("Notícias Específicas (ICL, Meu Timão, etc.)")
        
   
        filtered_df_specific = df_specific[
            df_specific['Tópico'].isin(selected_topics) &
            df_specific['Fonte'].isin(selected_sources)
        ]
        if search_title:
            filtered_df_specific = filtered_df_specific[filtered_df_specific['Título'].str.contains(search_title, case=False, na=False)]

 
        st.subheader(f"Exibindo {len(filtered_df_specific)} de {len(df_specific)} artigos específicos encontrados")
        for index, row in filtered_df_specific.iterrows():
            st.markdown(f"### [{row['Título']}]({row['URL']})")
            st.write(f"**Fonte:** {row['Fonte']} | **Tópico:** {row['Tópico']}")
            st.write(f"**Publicado em:** {row['published_at']}")
            st.divider() 

    with tab_generic:
        st.header("Notícias Gerais (Tecnologia, Esportes, etc.)")
        
        filtered_df_generic = df_generic[
            df_generic['Tópico'].isin(selected_topics) &
            df_generic['Fonte'].isin(selected_sources)
        ]
        if search_title:
            filtered_df_generic = filtered_df_generic[filtered_df_generic['Título'].str.contains(search_title, case=False, na=False)]

        st.subheader(f"Exibindo {len(filtered_df_generic)} de {len(df_generic)} artigos gerais encontrados")
        for index, row in filtered_df_generic.iterrows():
            st.markdown(f"### [{row['Título']}]({row['URL']})")
            st.write(f"**Fonte:** {row['Fonte']} | **Tópico:** {row['Tópico']}")
            st.write(f"**Publicado em:** {row['published_at']}")
            st.divider()