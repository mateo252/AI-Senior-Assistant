import uuid
import sqlite3
import chromadb
import pandas as pd
from chromadb.config import Settings
import os
import sys


class History:
    def __init__(self) -> None:
        
        self.is_chat = False
        self.history_path = os.path.join(
            os.path.dirname(os.path.abspath(sys.argv[0])),
            "history"
        )

        # Connections to SqliteDB
        sqlite_name = "history.db"
        self.sqlite_path = os.path.join(self.history_path, sqlite_name)
        
        self.db_conn = sqlite3.connect(self.sqlite_path, check_same_thread=False)
        self.db_cur = self.db_conn.cursor()
        self._create_sql_table()

        # Connections to ChromaDB 
        chroma_name = "history"
        self.chroma_client = chromadb.PersistentClient(
            path=self.history_path,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.chroma_client.get_or_create_collection(name=chroma_name)


    def save_to_chroma(self, description: str, metadata: dict) -> None:
        """Save image data to ChromaDB"""
        self.collection.add(
            documents=[description],
            metadatas=[metadata],
            ids=[str(uuid.uuid4())]
        )


    def read_from_chroma(self, description: str, n_results: int):
        """Get documents and metadata from the ChromaDB"""
        chroma_response = self.collection.query(
            query_texts=[description],
            n_results=n_results
        )
        return chroma_response["documents"], chroma_response["metadatas"]


    def _create_sql_table(self):
        """Create two table in sqliteDB"""
        self.db_cur.execute(
        """
        CREATE TABLE IF NOT EXISTS text_generator (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            created_at TEXT NOT NULL,
            model TEXT NOT NULL,
            eval_count REAL NOT NULL,            
            eval_duration REAL NOT NULL,
            load_duration REAL NOT NULL,
            prompt_eval_count REAL NOT NULL,
            prompt_eval_duration REAL NOT NULL,
            total_duration REAL NOT NULL,
            user_prompt TEXT NOT NULL,
            llm_content TEXT NOT NULL
        );
        """)
        self.db_conn.commit()


    def save_to_sqlite(self, data: dict) -> None:
        """Add statistics after the query to the model in Ollama"""
        df_data = pd.json_normalize(data)

        df_data.drop(columns=["done", "done_reason", "context", "message.role", "message.images"], inplace=True, errors="ignore")
        df_data.rename(columns={
            "response" : "llm_content",
            "message.content" : "llm_content"
        }, inplace=True)
        
        df_data.to_sql(
            name="text_generator",
            con=self.db_conn,
            if_exists="append",
            index=False
        )
        self.db_conn.commit()


    def read_from_sqlite(self) -> pd.DataFrame:
        """Download all data from the SqliteDB"""
        return pd.read_sql("SELECT * FROM text_generator;", self.db_conn)


    def on_close(self) -> None:
        """Closing open connections"""
        self.db_cur.close()
        self.db_conn.close()


