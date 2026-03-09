import fitz
import os
import re

class PDFKnowledgeBase:
    
    def __init__(self,path=None):
        if path is not None:
            self.path=path
        self.chunks=[]

    def load_pdf(self):
        for filename in os.listdir(self.path):
            if filename.endswith(".pdf"):
                full_path=os.path.join(self.path, filename)
                doc = fitz.open(full_path)
                print(f"📄 Loaded: {filename}, pages: {len(doc)}")
                for page in doc:
                    text = page.get_text()
                    # Split into chunks, for example by paragraph or every N lines
                    split_chunks = text.split("\n\n")  # or use `textwrap.wrap`, etc.
                    self.chunks.extend([chunk.strip() for chunk in split_chunks if chunk.strip()])

    def chunk_text(self, text):
        #Simple splitting by double newline or paragraphs
        return [chunk.strip() for chunk in text.split('\n\n') if chunk.strip()]
    def search(self, query, top_n=3):
        """
        Simple keyword-based search with basic scoring:
        - Counts occurrences of each query word
        - Gives a small boost for exact phrase matches
        - Rewards chunks containing multiple distinct query terms
        """
        if not query:
            return []

        query_lower = query.lower()
        query_words = [w for w in re.split(r"\W+", query_lower) if w]
        if not query_words:
            return []

        results = []
        for chunk in self.chunks:
            chunk_lower = chunk.lower()

            # Base score: total occurrences of individual words
            word_score = sum(chunk_lower.count(word) for word in query_words)
            if word_score == 0:
                continue

            # Distinct word coverage
            distinct_matches = sum(1 for word in set(query_words) if word in chunk_lower)

            # Exact phrase boost
            phrase_boost = 2 if query_lower in chunk_lower else 0

            score = word_score + distinct_matches + phrase_boost

            results.append(
                {
                    "text": chunk,
                    "score": score,
                }
            )

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_n]

if __name__ == "__main__":
    path="data/statutes"
    kb = PDFKnowledgeBase(path)
    kb.load_pdf()
    results = kb.search("tenant rights")  # try any keyword you saw in the output
    if not results:
        print("❌ No matching chunks found.")
    else:
        for i, (chunk, score) in enumerate(results, 1):
            print(f"\nResult {i} (Score: {score}):\n{chunk}...\n{'-'*40}")

