# AI Newsletter MVP

A personalized AI newsletter application built with Streamlit.

## Features

- 📰 Topic selection with multiple categories (AI, Machine Learning, Data Science, Technology)
- 📧 Email input for newsletter subscription
- 🎨 Modern UI with streamlit-shadcn-ui components
- ⚡ Fast and responsive interface

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Siddhant-Goswami/MVP-c5.git
   cd MVP-c5
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install streamlit streamlit-shadcn-ui
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Access the app**
   Open your browser and go to `http://localhost:8501`

## Project Structure

```
MVP-c5/
├── app.py              # Main Streamlit application
├── config/
│   └── sources.py      # News sources configuration
├── .gitignore          # Git ignore file
└── README.md           # This file
```

## Technologies Used

- **Streamlit** - Web application framework
- **streamlit-shadcn-ui** - UI component library
- **Python 3.10+** - Programming language

## Next Steps

- [ ] Implement backend newsletter generation
- [ ] Add email subscription functionality
- [ ] Integrate with news APIs
- [ ] Add user preferences and customization
- [ ] Deploy to cloud platform

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the [MIT License](LICENSE).
