import React from 'react';
import './HomePage.css';

const HomePage = () => {
  return (
    <div className="home-container">
      {/* Hero Section */}
      <section className="hero hero-bg-image">
        {/* Removed shape-1, shape-2, shape-3 for a cleaner look */}
        <div className="hero-content">
          <h1 className="hero-title">
            <span className="hello-yellow">Ace Your Exams with Confidence</span><br />
            <span className="username-highlight">Lamla AI: Your Exam Prep Superpower</span>
          </h1>
          <p className="hero-desc">
            Transform your notes into interactive quizzes and flashcards. Get instant feedback, track your progress, and study smarter—not harder. Lamla AI is your all-in-one exam preparation assistant.<br /><strong>Prep with purpose. Succeed with ease.</strong>
          </p>
          <div className="hero-btns">
            <a href="#signup" className="hero-btn">Get Started</a>
            <a href="#features" className="hero-btn secondary">Explore Features</a>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="features-section">
        <div className="shape-4"></div>
        <div className="shape-5"></div>
        <div className="section-header">
          <h2>Smart Features for <span className="highlight">Smart Students</span></h2>
          <p>Lamla-AI helps you prepare with purpose using these core features:</p>
        </div>
        <div className="features-grid">
          <a href="#custom_quiz" className="feature-card">
            <div className="feature-icon">📄</div>
            <h3 className="feature-title">Upload Study Materials</h3>
            <p className="feature-desc">Upload PDF or text-based materials. Content is extracted to power quiz generation.</p>
            <div className="feature-hint">Click to explore →</div>
          </a>
          <a href="#custom_quiz" className="feature-card">
            <div className="feature-icon">🧠</div>
            <h3 className="feature-title">AI Quiz Generator</h3>
            <p className="feature-desc">Automatically generates multiple-choice questions from your materials or typed content. Get instant feedback on your responses.</p>
            <div className="feature-hint">Click to explore →</div>
          </a>
          <a href="#dashboard" className="feature-card">
            <div className="feature-icon">📈</div>
            <h3 className="feature-title">Performance Tracking</h3>
            <p className="feature-desc">Tracks your score per quiz and uses color-coded indicators to highlight strong and weak areas.</p>
            <div className="feature-hint">Click to explore →</div>
          </a>
          <a href="#custom_quiz" className="feature-card">
            <div className="feature-icon">📚</div>
            <h3 className="feature-title">Subject + Topic Selection</h3>
            <p className="feature-desc">Select your subject or topic before quiz generation. Early foundation for syllabus-aware functionality.</p>
            <div className="feature-hint">Click to explore →</div>
          </a>
          <a href="#flashcards" className="feature-card">
            <div className="feature-icon">🃏</div>
            <h3 className="feature-title">Interactive Flashcards</h3>
            <p className="feature-desc">Create and study with AI-generated flashcards. Perfect for memorization and quick review sessions.</p>
            <div className="feature-hint">Click to explore →</div>
          </a>
          <a href="#exam_analyzer" className="feature-card">
            <div className="feature-icon">🔍</div>
            <h3 className="feature-title">Exam Analysis</h3>
            <p className="feature-desc">Analyze your uploaded exams or quizzes for instant feedback, topic breakdown, and personalized study recommendations. Turn your past tests into learning opportunities!</p>
            <div className="feature-hint">Click to explore →</div>
          </a>
        </div>
      </section>

      {/* Newsletter Section */}
      <section className="newsletter-section">
        <div className="newsletter-content">
          <h2 className="newsletter-title">Stay Ahead with Lamla-AI</h2>
          <p className="newsletter-desc">Subscribe for study tips, feature updates, and exclusive offers. Lamla-AI is your intelligent study assistant that helps you prepare with purpose.</p>
          <form className="newsletter-form" id="newsletterForm">
            <input type="email" className="newsletter-input" name="email" placeholder="Your Email" required aria-label="Email for newsletter" />
            <button type="submit" className="newsletter-btn">Subscribe</button>
          </form>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="testimonials-section">
        <div className="testimonial-content">
          <blockquote className="testimonial-quote">
            "Lamla-AI helped me turn my lecture slides into practice quizzes and flashcards in seconds. It's an amazing tool for exam preps!"
          </blockquote>
          <p className="testimonial-user">— Christopher N, Computer Science Student</p>
          <div className="testimonial-logo-row">
            <div className="testimonial-logo">UG</div>
            <div className="testimonial-logo">KNUST</div>
            <div className="testimonial-logo">UCC</div>
            <div className="testimonial-logo">UDS</div>
            <div className="testimonial-logo">UEW</div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage; 