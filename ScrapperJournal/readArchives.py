import sqlite3

# Nome do banco de dados (deve ser o mesmo do script principal)
DB_NAME = "my_journal.db"

def read_all_articles():
    """
    Conecta ao banco de dados e exibe todos os artigos da tabela 'articles'.
    """
    try:
        # 1. Conecta ao banco
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # 2. Executa uma consulta SQL para selecionar TUDO (*) da tabela 'articles'
        #    Ordena pelos mais recentes (data de publicação)
        print("Executando consulta: SELECT * FROM articles ORDER BY published_at DESC")
        cursor.execute("SELECT * FROM articles ORDER BY published_at DESC")
        
        # 3. Busca todos os resultados da consulta
        articles = cursor.fetchall()
        
        if not articles:
            print("O banco de dados está vazio. Execute o script 'my_journal.py' primeiro.")
            return

        print(f"\n--- Total de {len(articles)} artigos encontrados no banco de dados ---")
        
        # 4. Itera sobre cada resultado e imprime
        #    Cada 'article' é uma tupla com os dados na ordem das colunas
        #    (0=id, 1=title, 2=source_name, 3=url, 4=published_at, 5=topic, 6=fetched_at)
        
        for article in articles:
            print("\n--------------------------------------------------")
            print(f"ID: {article[0]}")
            print(f"Tópico: {article[5]}")
            print(f"Título: {article[1]}")
            print(f"Fonte: {article[2]}")
            print(f"URL: {article[3]}")
            print(f"Publicado em: {article[4]}")
            print("--------------------------------------------------")
            
    except sqlite3.Error as e:
        print(f"Ocorreu um erro ao ler o banco de dados: {e}")
    finally:
        # 5. Fecha a conexão
        if conn:
            conn.close()

# Executa a função principal
if __name__ == "__main__":
    read_all_articles()