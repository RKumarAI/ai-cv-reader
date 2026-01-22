import argparse
import sys
from pathlib import Path
from typing import List, Optional
import PyPDF2
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

class PDFReader:
    def __init__(self, api_key: Optional[str] = None):
        # If api_key is None, OpenAI will automatically look for OPENAI_API_KEY in env
        self.client = OpenAI(api_key=api_key)
        
        if not self.client.api_key:
            raise ValueError("OpenAI Key is Required. Set it in .env or pass it as an argument.")

    def extract_text(self, pdf_path: str) -> str:
        try:
            text = ""
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading PDF: {e}")

    def chunk_text(self, text: str, chunk_size: int = 4000) -> List[str]:
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0

        for word in words:
            # +1 accounts for the space
            if current_size + len(word) + 1 > chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk)) # FIXED: Space separator
                current_chunk = [word]
                current_size = len(word)
            else:
                current_chunk.append(word)
                current_size += len(word) + 1

        if current_chunk:
            chunks.append(" ".join(current_chunk))
        return chunks

    def summarize_chunk(self, chunk: str, max_words: int = 200) -> str:
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini", # Use 4o-mini (faster/cheaper than 3.5)
                messages=[
                    {
                        "role": "system", 
                        "content": f"Summarize the following CV text in {max_words} words or less. Focus on skills, experience, and education."
                    },
                    {"role": "user", "content": chunk}
                ],
                max_tokens=400,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error during AI processing: {e}"

    def summarize_pdf(self, pdf_path: str, max_words: int = 200, chunk_size: int = 4000) -> str:
        print(f"Reading: {pdf_path}")
        text = self.extract_text(pdf_path)

        if not text:
            return "No readable text found in PDF."

        if len(text) <= chunk_size:
            return self.summarize_chunk(text, max_words)

        chunks = self.chunk_text(text, chunk_size)
        summaries = []
        
        # Determine how many words each chunk gets to contribute
        chunk_max = max(50, max_words // len(chunks))

        for i, chunk in enumerate(chunks, 1):
            print(f"Processing part {i}/{len(chunks)}...")
            summaries.append(self.summarize_chunk(chunk, chunk_max))

        combined_output = " ".join(summaries)
        
        # FIXED: Check word count, not character count
        if len(combined_output.split()) > max_words:
            return self.summarize_chunk(combined_output, max_words)

        return combined_output

def main():
    parser = argparse.ArgumentParser(description="AI CV Reader")
    parser.add_argument("pdf_path", help="Path to the PDF File")
    parser.add_argument("-l", "--max_length", type=int, default=200)
    parser.add_argument("-o", "--output", help="Output file path") # Changed to -o
    parser.add_argument("-c", "--chunk-size", type=int, default=4000)
    parser.add_argument("--api-key", help="OpenAI key")

    args = parser.parse_args()

    if not Path(args.pdf_path).exists():
        print(f"❌ File not found: {args.pdf_path}")
        sys.exit(1)

    try:
        reader = PDFReader(api_key=args.api_key)
        summary = reader.summarize_pdf(
            args.pdf_path, 
            max_words=args.max_length, 
            chunk_size=args.chunk_size
        )

        print("\n--- CV SUMMARY ---\n")
        print(summary)

        if args.output:
            Path(args.output).write_text(summary, encoding="utf-8")
            print(f"\n Summary saved to {args.output}")

    except Exception as e:
        print(f"❌ Critical Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()