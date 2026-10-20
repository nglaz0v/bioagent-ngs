import json
import faiss
import numpy as np
from typing import List, Dict, Optional
from openai import OpenAI
import os

class RAGEngine:
    def __init__(self, knowledge_base_path: str = "data/knowledge_base.jsonl", index_path: str = "data/faiss.index"):
        self.knowledge_base_path = knowledge_base_path
        self.index_path = index_path
        self.chunks = []
        self.embeddings = []
        self.index = None

        api_key = os.environ.get("OPENAI_API_KEY")
        base_url = os.environ.get("OPENAI_BASE_URL")
        self.embedding_model = os.environ.get("OPENAI_EMBEDDING_MODEL")
        
        # OpenAI клиент для эмбеддингов (дешевле, чем Anthropic embeddings)
        self.openai_client = OpenAI(api_key=api_key, base_url=base_url)
        
        self._load_or_build_index()
    
    def _load_or_build_index(self):
        """Загружает существующий индекс или строит новый"""
        if os.path.exists(self.index_path) and os.path.exists(f"{self.index_path}.chunks"):
            print("Loading existing FAISS index...")
            self.index = faiss.read_index(self.index_path)
            with open(f"{self.index_path}.chunks", 'r', encoding='utf-8') as f:
                self.chunks = json.load(f)
        else:
            print("Building new FAISS index...")
            self._build_index()
    
    def _build_index(self):
        """Строит FAISS индекс из knowledge base"""
        # Читаем чанки
        with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
            for line in f:
                self.chunks.append(json.loads(line))
        
        print(f"Generating embeddings for {len(self.chunks)} chunks...")
        
        # Генерируем эмбеддинги батчами (OpenAI limit: 2048 за раз)
        batch_size = 100
        all_embeddings = []
        
        for i in range(0, len(self.chunks), batch_size):
            batch = self.chunks[i:i+batch_size]
            texts = [chunk['content'] for chunk in batch]
            
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)
            
            if i % 500 == 0:
                print(f"Processed {i}/{len(self.chunks)} chunks...")
        
        self.embeddings = np.array(all_embeddings).astype('float32')
        
        # Создаем FAISS индекс
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings)
        
        # Сохраняем
        faiss.write_index(self.index, self.index_path)
        with open(f"{self.index_path}.chunks", 'w', encoding='utf-8') as f:
            json.dump(self.chunks, f, ensure_ascii=False)
        
        print(f"✅ FAISS index built and saved to {self.index_path}")
    
    def retrieve_relevant_context(
        self, 
        query: str, 
        top_k: int = 5, 
        category_filter: Optional[str] = None,
        tool_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Ищет релевантные чанки в базе знаний
        
        Args:
            query: Запрос пользователя
            top_k: Количество возвращаемых чанков
            category_filter: Фильтр по категории (tool_reference/best_practices/code_examples/troubleshooting)
            tool_filter: Фильтр по имени утилиты (gatk/fgbio/bwa-mem2 и т.д.)
        
        Returns:
            Список чанков с метаданными
        """
        # Генерируем эмбеддинг для запроса
        response = self.openai_client.embeddings.create(
            model=self.embedding_model,
            input=[query]
        )
        query_embedding = np.array([response.data[0].embedding]).astype('float32')
        
        # Поиск в FAISS
        distances, indices = self.index.search(query_embedding, min(top_k * 3, len(self.chunks)))
        
        # Фильтруем результаты
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx == -1:  # FAISS возвращает -1 если меньше результатов чем top_k
                continue
            
            chunk = self.chunks[idx]
            
            # Применяем фильтры
            if category_filter and chunk['category'] != category_filter:
                continue
            if tool_filter and chunk['tool_name'] != tool_filter:
                continue
            
            results.append({
                **chunk,
                'distance': float(distance),
                'relevance_score': 1 / (1 + distance)  # Нормализуем distance в score
            })
            
            if len(results) >= top_k:
                break
        
        # Сортируем по релевантности
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return results[:top_k]

# Глобальный экземпляр (инициализируется один раз при старте)
rag_engine = None

def get_rag_engine() -> RAGEngine:
    global rag_engine
    if rag_engine is None:
        rag_engine = RAGEngine()
    return rag_engine
