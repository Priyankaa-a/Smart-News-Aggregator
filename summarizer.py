from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import re

# Check if GPU is available
device = 0 if torch.cuda.is_available() else -1

class ArticleSummarizer:
    def __init__(self, use_ai=True):
        """
        Initialize summarization pipeline with better model.
        
        Models available:
        1. facebook/bart-large-cnn (faster, good quality)
        2. google/pegasus-cnn_dailymail (better quality, slower)
        3. t5-base (balanced)
        """
        self.use_ai = use_ai
        self.summarizer = None
        
        if use_ai:
            try:
                # Using PEGASUS (better quality than BART)
                print("🤖 Loading PEGASUS summarization model...")
                self.summarizer = pipeline(
                    "summarization",
                    model="google/pegasus-cnn_dailymail",
                    device=device,
                    framework="pt"
                )
                print("✅ PEGASUS Summarizer loaded successfully!")
            except Exception as e:
                print(f"⚠️ Could not load PEGASUS: {e}")
                print("Falling back to BART...")
                try:
                    self.summarizer = pipeline(
                        "summarization",
                        model="facebook/bart-large-cnn",
                        device=device,
                        framework="pt"
                    )
                    print("✅ BART Summarizer loaded successfully!")
                except Exception as e2:
                    print(f"❌ Could not load any model: {e2}")
                    self.use_ai = False
    
    def summarize(self, text, num_sentences=3):
        """
        Summarize article text with quality checks.
        
        Args:
            text: Article content
            num_sentences: Target number of sentences (2-5)
        
        Returns:
            Summarized text or fallback
        """
        text = text.strip()
        
        # Handle empty/short text
        if not text or len(text) < 100:
            return text[:300] + "..." if len(text) > 300 else text
        
        # Use AI summarization if available
        if self.use_ai and self.summarizer:
            return self._ai_summarize(text, num_sentences)
        else:
            return self._simple_summarize(text, num_sentences)
    
    def _ai_summarize(self, text, num_sentences=3):
        """Use transformer-based AI summarization with quality checks."""
        try:
            # Limit input to avoid memory issues
            words = text.split()
            
            # BART/PEGASUS need minimum input
            if len(words) < 50:
                return self._simple_summarize(text, num_sentences)
            
            # Limit to 1024 words
            if len(words) > 1024:
                text = " ".join(words[:1024])
            
            # Calculate summary length based on input
            input_length = len(text.split())
            
            # Dynamic length calculation
            max_length = max(80, min(200, input_length // 4))  # 25% of input
            min_length = max(40, max_length // 2)  # At least 50% of max
            
            # Generate summary
            summary = self.summarizer(
                text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False,
                truncation=True
            )
            
            result = summary[0]['summary_text']
            
            # Quality check: if summary is too short or just repeats headline
            if len(result.split()) < 15:
                return self._simple_summarize(text, num_sentences)
            
            return result
            
        except Exception as e:
            print(f"Error in AI summarization: {e}")
            return self._simple_summarize(text, num_sentences)
    
    def _simple_summarize(self, text, num_sentences=3):
        """Fallback: Extract first N sentences with quality."""
        # Split by period, question mark, exclamation
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return text[:200] + "..."
        
        # Take first N sentences
        summary_sentences = sentences[:num_sentences]
        summary = '. '.join(summary_sentences)
        
        # Ensure it ends with period
        if summary and not summary.endswith('.'):
            summary += '.'
        
        # Limit total length
        if len(summary) > 300:
            summary = summary[:300] + "..."
        
        return summary if summary else text[:200] + "..."