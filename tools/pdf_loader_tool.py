import os
from typing import Dict, Any, List, Optional
from PyPDF2 import PdfReader


class PDFLoaderTool:
    """Tool for loading and parsing PDF documents as context/prompts for the LLM."""
    
    name = "pdf_loader"
    description = "Load and parse PDF documents to extract text content for LLM context"
    
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        self.loaded_documents: Dict[str, str] = {}
        os.makedirs(upload_dir, exist_ok=True)
    
    def load_pdf(self, file_path: str) -> Dict[str, Any]:
        """Load a single PDF file and extract its text content."""
        try:
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': f'File not found: {file_path}'
                }
            
            reader = PdfReader(file_path)
            text_content = []
            
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_content.append(f"--- Page {page_num} ---\n{page_text}")
            
            full_text = "\n\n".join(text_content)
            filename = os.path.basename(file_path)
            self.loaded_documents[filename] = full_text
            
            return {
                'success': True,
                'filename': filename,
                'page_count': len(reader.pages),
                'character_count': len(full_text),
                'content': full_text,
                'message': f"Successfully loaded {filename} ({len(reader.pages)} pages)"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to load PDF: {file_path}'
            }
    
    def load_multiple_pdfs(self, file_paths: List[str]) -> Dict[str, Any]:
        """Load multiple PDF files."""
        results = []
        successful = 0
        failed = 0
        
        for file_path in file_paths:
            result = self.load_pdf(file_path)
            results.append({
                'file': file_path,
                'success': result['success'],
                'message': result.get('message', result.get('error', ''))
            })
            if result['success']:
                successful += 1
            else:
                failed += 1
        
        return {
            'success': failed == 0,
            'total': len(file_paths),
            'successful': successful,
            'failed': failed,
            'results': results,
            'message': f"Loaded {successful}/{len(file_paths)} PDFs successfully"
        }
    
    def get_loaded_documents(self) -> Dict[str, Any]:
        """Get list of all loaded documents."""
        return {
            'success': True,
            'documents': list(self.loaded_documents.keys()),
            'count': len(self.loaded_documents),
            'message': f"{len(self.loaded_documents)} documents loaded"
        }
    
    def get_document_content(self, filename: str) -> Dict[str, Any]:
        """Get content of a specific loaded document."""
        if filename not in self.loaded_documents:
            return {
                'success': False,
                'error': f'Document not loaded: {filename}'
            }
        
        content = self.loaded_documents[filename]
        return {
            'success': True,
            'filename': filename,
            'content': content,
            'character_count': len(content)
        }
    
    def get_combined_context(self, filenames: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get combined content from multiple documents as context for LLM."""
        try:
            if filenames:
                docs_to_combine = {k: v for k, v in self.loaded_documents.items() if k in filenames}
            else:
                docs_to_combine = self.loaded_documents
            
            if not docs_to_combine:
                return {
                    'success': False,
                    'error': 'No documents available to combine'
                }
            
            combined_parts = []
            for filename, content in docs_to_combine.items():
                combined_parts.append(f"=== Document: {filename} ===\n{content}")
            
            combined_content = "\n\n".join(combined_parts)
            
            return {
                'success': True,
                'documents_included': list(docs_to_combine.keys()),
                'content': combined_content,
                'character_count': len(combined_content),
                'message': f"Combined {len(docs_to_combine)} documents"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def clear_documents(self) -> Dict[str, Any]:
        """Clear all loaded documents from memory."""
        count = len(self.loaded_documents)
        self.loaded_documents.clear()
        return {
            'success': True,
            'message': f"Cleared {count} documents from memory"
        }
    
    def save_uploaded_file(self, file_storage, filename: str) -> Dict[str, Any]:
        """Save an uploaded file to the upload directory."""
        try:
            file_path = os.path.join(self.upload_dir, filename)
            file_storage.save(file_path)
            return {
                'success': True,
                'file_path': file_path,
                'message': f"File saved: {filename}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def run(self, action: str, **kwargs) -> Dict[str, Any]:
        """Main entry point for the tool."""
        actions = {
            'load': lambda: self.load_pdf(kwargs.get('file_path', '')),
            'load_multiple': lambda: self.load_multiple_pdfs(kwargs.get('file_paths', [])),
            'list': self.get_loaded_documents,
            'get_content': lambda: self.get_document_content(kwargs.get('filename', '')),
            'get_context': lambda: self.get_combined_context(kwargs.get('filenames')),
            'clear': self.clear_documents
        }
        
        if action not in actions:
            return {'success': False, 'error': f'Unknown action: {action}'}
        
        return actions[action]() if callable(actions[action]) else actions[action]
