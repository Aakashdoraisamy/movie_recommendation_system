
# 🎬 Movie Recommendation System
<p align="center">
  <img src="https://img.shields.io/badge/Django-5.2-green?logo=django" alt="Django">
  <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/MySQL-Database-orange?logo=mysql" alt="MySQL">
</p>

## ✨ Overview
A modern, secure, and scalable web application for movie search, rating, and recommendations. Built with Django and powered by machine learning, it leverages real-world movie data and offers a professional user experience.

---

## 🎯 What does it do?
- 🔎 **Search:** Find movies by title, genre, or cast
- ⭐ **Rate:** Submit and view your ratings for any movie
- 🖼️ **Details:** See posters, cast, genres, and overviews
- 📥 **Bulk Import:** Load thousands of movies from TMDB datasets
- 🤖 **ML-Powered Recommendations:** Get movie suggestions using content-based filtering (matching movies by genres, cast, and features you like)
- 🔒 **Security:** All secrets managed via `.env` (never exposed)

---

## 🛠️ How does it work?
1. **Data Import:**
   - Custom Django command loads and merges TMDB movie and credits data into MySQL
2. **Search & Discovery:**
   - Users search by keywords, genres, or cast; results are instant and relevant
3. **Movie Details & Ratings:**
   - Each movie page shows rich details and allows user ratings
4. **Machine Learning Core:**
   - The recommendation engine uses content-based filtering: it analyzes the genres, cast, and features of movies you rate highly, then suggests similar movies using ML algorithms (scikit-learn, pandas).
   - **Algorithms Used:**
     - Cosine similarity and vectorization to compare movie features
     - Feature extraction from genres, cast, and keywords
     - Ranking and filtering to deliver personalized results
   - **Workflow:**
     1. User rates movies
     2. System builds a profile of preferred genres, cast, and features
     3. Movies with similar profiles are recommended using ML techniques
   - **Future Directions:**
     - Easily extendable to collaborative filtering (user-user or item-item)
     - Can integrate deep learning for advanced recommendations
     - Ready for hybrid approaches combining multiple ML strategies
5. **Security:**
   - Secrets and credentials are stored in `.env`, following best practices
6. **UI:**
   - Responsive, Bootstrap-powered templates for a clean, modern look

---

## 🏗️ What did we build?
- Django models for movies, ratings, and search logs
- Management command for bulk data import
- Content-based movie recommendation logic using scikit-learn and pandas
- Secure settings using `python-dotenv`
- Templates for home, search, and detail pages
- Scalable backend ready for advanced ML features and more

---

## 🚦 How to use it?
1. Install dependencies and configure `.env`
2. Import movie data from CSVs
3. Run the Django server
4. Search, browse, and rate movies in your browser

---
