# News sources configuration for the AI Newsletter MVP

NEWS_SOURCES = {
    'AI': {
        'name': 'Artificial Intelligence',
        'web_sources': [
            'https://openai.com/blog/',
            'https://www.anthropic.com/news',
            'https://www.deepmind.com/blog',
            'https://blog.google/technology/ai/',
            'https://aws.amazon.com/blogs/machine-learning/',
        ],
        'rss_sources': [
            'https://feeds.feedburner.com/oreilly/radar',
            'https://blog.google/technology/ai/rss/',
            'https://aws.amazon.com/blogs/machine-learning/feed/',
            'https://distill.pub/rss.xml',
        ],
        'api_sources': [
            'https://hn.algolia.com/api/v1/search_by_date?query=AI&tags=story&hitsPerPage=10',
            'https://www.reddit.com/r/artificial/hot.json?limit=5',
            'http://export.arxiv.org/api/query?search_query=cat:cs.AI&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending',
        ]
    },
    'Machine Learning': {
        'name': 'Machine Learning',
        'web_sources': [
            'https://distill.pub/',
            'https://blog.tensorflow.org/',
            'https://pytorch.org/blog/',
            'https://scikit-learn.org/stable/whats_new.html',
        ],
        'rss_sources': [
            'https://blog.tensorflow.org/feeds/posts/default',
            'https://pytorch.org/feed.xml',
            'https://scikit-learn.org/stable/whats_new.html',
        ],
        'api_sources': [
            'https://hn.algolia.com/api/v1/search_by_date?query=machine+learning&tags=story&hitsPerPage=10',
            'https://www.reddit.com/r/MachineLearning/hot.json?limit=5',
            'http://export.arxiv.org/api/query?search_query=cat:cs.LG&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending',
        ]
    },
    'Data Science': {
        'name': 'Data Science',
        'web_sources': [
            'https://towardsdatascience.com/',
            'https://www.kaggle.com/blog',
            'https://blog.paperspace.com/',
            'https://www.datacamp.com/blog',
        ],
        'rss_sources': [
            'https://towardsdatascience.com/feed',
            'https://www.kaggle.com/blog/rss',
            'https://blog.paperspace.com/feed/',
            'https://www.datacamp.com/blog/feed/',
        ],
        'api_sources': [
            'https://hn.algolia.com/api/v1/search_by_date?query=data+science&tags=story&hitsPerPage=10',
            'https://www.reddit.com/r/datascience/hot.json?limit=5',
        ]
    },
    'Technology': {
        'name': 'Technology',
        'web_sources': [
            'https://techcrunch.com/',
            'https://www.theverge.com/',
            'https://arstechnica.com/',
            'https://www.wired.com/',
        ],
        'rss_sources': [
            'https://techcrunch.com/feed/',
            'https://www.theverge.com/rss/index.xml',
            'https://feeds.arstechnica.com/arstechnica/index/',
            'https://www.wired.com/feed/rss',
        ],
        'api_sources': [
            'https://hn.algolia.com/api/v1/search_by_date?query=technology&tags=story&hitsPerPage=10',
            'https://www.reddit.com/r/technology/hot.json?limit=5',
        ]
    }
}
