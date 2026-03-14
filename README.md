# IntelliDigest: AI-Powered Smart News Aggregator

**IntelliDigest** is a sophisticated news aggregation platform that crawls multiple sources, clusters related topics, and provides concise, AI-generated summaries. Designed with a modern, high-contrast interface, it helps users stay informed without the clutter of traditional news sites.

## 🚀 Features

* **Real-time Scraping:** Dynamically fetches latest news from multiple reliable sources.
* **AI Summarization:** Utilizes the `google/pegasus-cnn_dailymail` model via Hugging Face Transformers for high-quality abstractive summaries.
* **Smart Clustering:** Automatically groups similar news stories using machine learning to avoid redundancy.
* **Modern UI:** A sleek, dark-themed dashboard built for high readability and a premium user experience.
* **Local Database:** Efficiently stores and manages news data using SQLite.

## 🛠️ Tech Stack

* **Language:** Python 3.x
* **Frontend:** Streamlit
* **NLP Models:** PEGASUS (Transformers), PyTorch
* **Database:** SQLite
* **Scraping:** BeautifulSoup4 / Requests

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Priyankaa-a/IntelliDigest.git](https://github.com/Priyankaa-a/IntelliDigest.git)
   cd IntelliDigest

   📂 Project Structure
app.py: Main entry point for the web interface.

summarizer.py: Logic for AI summarization using Transformers.

scraper.py: Web scraping scripts for news collection.

clustering.py: Machine learning logic for grouping news articles.

db.py: Database schema and connection management.

utils.py: Helper functions for data processing.

🛡️ License
Distributed under the MIT License.
