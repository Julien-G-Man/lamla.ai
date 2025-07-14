from django.core.management.base import BaseCommand
from slides_analyzer.models import ChatbotKnowledge

class Command(BaseCommand):
    help = 'Populate the chatbot knowledge base with information about Lamla AI'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Populating chatbot knowledge base...'))
        
        # Clear existing knowledge
        ChatbotKnowledge.objects.all().delete()
        
        # Define knowledge base entries
        knowledge_entries = [
            {
                'category': 'what_is',
                'question': 'What is Lamla AI?',
                'answer': 'Lamla AI stands for "Learn And Master Like an Ace" - it\'s a smart exam preparation assistant designed to help students study with intention, not panic! 🎯\n\n**What we do:**\n• AI-powered learning platform\n• Generate personalized quizzes from your study materials\n• Create interactive flashcards\n• Provide detailed performance analytics\n• Help you study smarter, not harder\n\nOur motto is "Study Smarter. Perform Better." - we\'re here to make your learning journey more effective and less stressful!',
                'keywords': 'lamla, what is, definition, purpose, meaning'
            },
            {
                'category': 'platform_navigation',
                'question': 'How do I navigate the Lamla AI platform?',
                'answer': 'Great question! Let me guide you through our platform navigation: 🧭\n\n**Main Sections:**\n• **Home** - Overview and getting started\n• **Custom Quiz** - Upload materials and generate quizzes\n• **Flashcards** - Create study flashcards\n• **Exam Analyzer** - Analyze exam content\n• **Dashboard** - View your progress and stats\n• **User Profile** - Manage your account\n• **About** - Learn more about the platform\n• **Contact** - Get support\n\n**How to navigate:**\n1. Use the navigation menu at the top of the page\n2. Click on any section to explore\n3. Each section has clear instructions\n4. You can always return to the home page\n\nEverything is designed to be intuitive and user-friendly! 😊',
                'keywords': 'navigation, menu, sections, pages, where to go, platform layout'
            },
            {
                'category': 'custom_quiz',
                'question': 'How do I use the Custom Quiz feature?',
                'answer': 'The Custom Quiz feature is one of our most popular tools! Here\'s how to use it: 📝\n\n**Step-by-Step Process:**\n1. **Go to Custom Quiz** - Click "Custom Quiz" in the navigation menu\n2. **Upload Materials** - Upload your study files (PDF, PPTX, or text)\n3. **Set Parameters** - Choose:\n   • Number of multiple-choice questions\n   • Number of short-answer questions\n   • Quiz time limit\n4. **Generate Quiz** - Click "Generate Quiz" to create personalized questions\n5. **Take the Quiz** - Answer questions within the time limit\n6. **Review Results** - Get instant feedback with detailed explanations\n\n**Pro Tips:**\n• Start with 3-5 questions to get familiar\n• Use a mix of question types for better learning\n• Review explanations to understand concepts better\n\nReady to create your first quiz? 🚀',
                'keywords': 'custom quiz, quiz creation, upload files, generate questions, take quiz'
            },
            {
                'category': 'flashcards_feature',
                'question': 'How do I create and use flashcards?',
                'answer': 'Flashcards are an amazing study tool! Here\'s how to create and use them: 🗂️\n\n**Creating Flashcards:**\n1. **Go to Flashcards** - Click "Flashcards" in the navigation\n2. **Upload Materials** - Upload your study files\n3. **Choose Type** - Select from:\n   • **General** - Mixed content\n   • **Concepts** - Terms and definitions\n   • **Processes** - Step-by-step procedures\n4. **Set Number** - Choose how many flashcards you want\n5. **Generate** - Click "Generate Flashcards"\n\n**Using Flashcards:**\n• **Flip through** - Click to see questions and answers\n• **Study actively** - Test yourself before flipping\n• **Review regularly** - Use spaced repetition\n• **Focus on weak areas** - Mark cards you need to review\n\n**Why Flashcards Work:**\n• Active recall strengthens memory\n• Visual learning aids retention\n• Quick review sessions\n• Perfect for on-the-go studying\n\nStart creating your flashcards today! 📚',
                'keywords': 'flashcards, create flashcards, study cards, flip cards, concepts'
            },
            {
                'category': 'exam_analyzer',
                'question': 'What is the Exam Analyzer and how do I use it?',
                'answer': 'The Exam Analyzer is your secret weapon for exam preparation! 🎯\n\n**What it does:**\n• Analyzes your exam materials\n• Generates practice questions based on your content\n• Helps you focus on specific exam topics\n• Provides targeted preparation\n\n**How to use it:**\n1. **Go to Exam Analyzer** - Click in the navigation menu\n2. **Enter Subject** - Specify your exam topic\n3. **Upload Materials** - Add your exam content (PDF, PPTX, or text)\n4. **Set Questions** - Choose how many practice questions you want\n5. **Analyze** - Click "Analyze" to generate questions\n6. **Practice** - Take the generated quiz\n\n**Benefits:**\n• **Targeted Practice** - Questions match your exam content\n• **Focused Study** - No generic questions\n• **Better Preparation** - Understand what to expect\n• **Confidence Building** - Practice with similar content\n\nPerfect for those important exams! 📖',
                'keywords': 'exam analyzer, analyze exams, exam preparation, practice questions'
            },
            {
                'category': 'dashboard',
                'question': 'What can I see on my Dashboard?',
                'answer': 'Your Dashboard is your personal learning command center! 📊\n\n**Dashboard Features:**\n• **Recent Activity** - Your latest study sessions\n• **Statistics** - Progress and performance metrics\n• **Profile Information** - Quick access to your details\n• **Feedback History** - Your recent feedback submissions\n• **Contact Submissions** - Messages you\'ve sent\n• **Subscription Status** - Newsletter preferences\n• **Join Date** - How long you\'ve been with us\n• **Recent Questions** - Questions from your study sessions\n\n**What you can track:**\n• Study session frequency\n• Quiz performance trends\n• Areas for improvement\n• Overall progress\n• Account activity\n\n**Access:**\n• Click "Dashboard" in the navigation menu\n• View anytime to check your progress\n• Great for staying motivated!\n\nYour learning journey, all in one place! 🎉',
                'keywords': 'dashboard, profile, statistics, progress, account management'
            },
            {
                'category': 'user_profile',
                'question': 'How do I manage my User Profile?',
                'answer': 'Your User Profile is where you personalize your Lamla AI experience! 👤\n\n**Profile Management Steps:**\n1. **Access Profile** - Click "User Profile" in navigation\n2. **Edit Information** - Update:\n   • First and last name\n   • Email address\n   • Personal bio\n3. **Upload Picture** - Add a profile photo:\n   • Supported: JPG, PNG, GIF\n   • Maximum size: 5MB\n   • Will appear across the platform\n4. **View Statistics** - See your:\n   • Total feedback submissions\n   • Contact form submissions\n   • Subscription status\n5. **Save Changes** - Click save to update your profile\n\n**Profile Benefits:**\n• **Personalization** - Make the platform yours\n• **Recognition** - Your picture appears everywhere\n• **Tracking** - Monitor your activity\n• **Professional Look** - Complete your profile\n\nMake it uniquely yours! ✨',
                'keywords': 'user profile, edit profile, profile picture, account settings, personal info'
            },
            {
                'category': 'file_upload',
                'question': 'How do I upload study materials?',
                'answer': 'Uploading study materials is super easy! 📁\n\n**Upload Methods:**\n• **Drag & Drop** - Simply drag files into the upload area\n• **Click to Browse** - Click the upload area to select files\n• **Paste Text** - Copy and paste text directly\n\n**Supported File Types:**\n• **PDF** (.pdf) - Lecture notes, textbooks, research papers\n• **PowerPoint** (.pptx) - Slides, presentations\n• **Text Files** (.txt) - Notes, summaries\n\n**File Requirements:**\n• Maximum size: 10MB per file\n• Clear, readable text content\n• Well-structured documents work best\n\n**Upload Process:**\n1. Go to Custom Quiz, Flashcards, or Exam Analyzer\n2. Click the upload area or drag files\n3. Select your study materials\n4. Wait for text extraction\n5. Review extracted content\n6. Generate quizzes or flashcards\n\n**Pro Tips:**\n• Use clear, well-formatted documents\n• Ensure text is readable (not scanned images)\n• Combine multiple files for comprehensive coverage\n\nReady to upload your materials? 📚',
                'keywords': 'upload files, file upload, supported formats, drag and drop, text extraction'
            },
            {
                'category': 'quiz_taking',
                'question': 'How do I take quizzes and see results?',
                'answer': 'Taking quizzes is both fun and educational! 🎯\n\n**Quiz Taking Process:**\n1. **Generate Quiz** - Create from your study materials\n2. **Set Timer** - Choose time limit (default: 10 minutes)\n3. **Answer Questions** - Two types:\n   • **Multiple Choice** - Select A, B, C, or D\n   • **Short Answer** - Type your responses\n4. **Submit** - Finish when done or time expires\n5. **View Results** - Get detailed feedback\n\n**Results Include:**\n• **Score Percentage** - How well you performed\n• **Correct/Incorrect** - Question-by-question breakdown\n• **Detailed Explanations** - Why answers are correct\n• **Performance Analytics** - Visual charts and insights\n• **Improvement Suggestions** - Areas to focus on\n\n**Pro Tips:**\n• Read questions carefully\n• Use the timer wisely\n• Review explanations for learning\n• Don\'t panic - it\'s practice!\n\nEvery quiz is a learning opportunity! 📈',
                'keywords': 'take quiz, quiz results, score, feedback, explanations, performance'
            },
            {
                'category': 'feedback_system',
                'question': 'How does the feedback system work?',
                'answer': 'Your feedback helps us make Lamla AI even better! 💬\n\n**Feedback Opportunities:**\n• **After Quizzes** - Rate your experience and provide comments\n• **Contact Forms** - Submit detailed feedback\n• **About Page** - Use the contact form\n• **Direct Email** - Send to support@lamla.ai\n\n**What Happens to Feedback:**\n• **Sent to Support** - Goes to support@lamla.ai\n• **Reviewed Regularly** - We read every submission\n• **Improves Platform** - Your suggestions shape updates\n• **Stored Securely** - Your privacy is protected\n\n**Feedback Types:**\n• **Quiz Experience** - How was your quiz?\n• **Feature Requests** - What would you like to see?\n• **Bug Reports** - Found an issue?\n• **General Comments** - Any thoughts?\n\n**View Your Feedback:**\n• Check Dashboard for history\n• See in User Profile\n• Track your submissions\n\nYour voice matters! 🎤',
                'keywords': 'feedback, rating, suggestions, improvement, contact support'
            },
            {
                'category': 'account_management',
                'question': 'How do I manage my account?',
                'answer': 'Managing your account is straightforward and secure! 🔐\n\n**Account Features:**\n• **Sign Up/Login** - Easy registration and access\n• **Profile Management** - Edit personal information\n• **Dashboard Access** - View statistics and progress\n• **Newsletter Subscription** - Stay updated\n• **Feedback System** - Submit suggestions\n• **Study History** - Track your learning journey\n\n**Account Management Steps:**\n1. **Access Settings** - Use navigation menu\n2. **Edit Profile** - Update personal information\n3. **View Statistics** - Check your progress\n4. **Manage Subscriptions** - Control email preferences\n5. **Submit Feedback** - Share your thoughts\n6. **Track Progress** - Monitor your learning\n\n**Security Features:**\n• Secure login system\n• Password protection\n• Privacy controls\n• Data protection\n\n**Account Benefits:**\n• Personalized experience\n• Progress tracking\n• Study history\n• Customized content\n\nYour learning journey, your way! 🚀',
                'keywords': 'account, login, signup, logout, manage account, settings'
            },
            {
                'category': 'contact_support',
                'question': 'How can I get help and support?',
                'answer': 'We\'re here to help you succeed! 🆘\n\n**Support Options:**\n• **AI Assistant** - That\'s me! Ask me anything\n• **Email Support** - contact.lamla1@gmail.com\n• **Contact Form** - Use the Contact page\n• **Feedback System** - After quizzes\n• **About Page** - Detailed contact form\n\n**What We Help With:**\n• **Technical Issues** - Platform problems\n• **Feature Questions** - How to use tools\n• **Account Issues** - Login, profile, settings\n• **General Inquiries** - Any questions\n• **Bug Reports** - Found an issue?\n\n**Response Times:**\n• **AI Assistant** - Instant responses\n• **Email Support** - Within 24 hours\n• **Contact Forms** - Within 48 hours\n\n**Before Contacting:**\n• Check our FAQ sections\n• Try the AI assistant first\n• Be specific about your issue\n• Include relevant details\n\nWe\'re committed to your success! 💪',
                'keywords': 'support, help, contact, email, feedback, assistance'
            },
            {
                'category': 'features',
                'question': 'What features does Lamla AI offer?',
                'answer': 'Lamla AI is packed with powerful features to supercharge your learning! ⚡\n\n**Core Features:**\n• **Custom Quiz Generation** - AI-powered questions from your materials\n• **Interactive Flashcards** - Study cards for key concepts\n• **Exam Analyzer** - Analyze and prepare for specific exams\n• **Performance Tracking** - Detailed analytics and progress\n• **User Profiles** - Personalize your experience\n• **File Upload** - Support for PDF, PPTX, and text\n• **Instant Feedback** - Get explanations and suggestions\n• **Dashboard Analytics** - Track your progress\n\n**Study Tools:**\n• **Multiple Question Types** - MCQs and short answers\n• **Timer Settings** - Customizable quiz times\n• **Progress Tracking** - Visual performance charts\n• **Study History** - Review past sessions\n• **Personalized Content** - Based on your materials\n\n**Platform Features:**\n• **Responsive Design** - Works on all devices\n• **Secure Uploads** - Your data is protected\n• **Easy Navigation** - Intuitive interface\n• **Comprehensive Support** - Multiple help options\n\nEverything you need to study smarter! 🎓',
                'keywords': 'features, capabilities, what can it do, tools, functions'
            },
            {
                'category': 'how_to',
                'question': 'How do I get started with Lamla AI?',
                'answer': 'Welcome to Lamla AI! Let\'s get you started on your learning journey! 🚀\n\n**Getting Started Steps:**\n1. **Create Account** - Sign up using the login/signup button\n2. **Explore Platform** - Take a tour of the main sections\n3. **Upload Materials** - Go to "Custom Quiz" and upload your first study files\n4. **Generate Content** - Create your first quiz or flashcards\n5. **Take a Quiz** - Experience the platform with a practice quiz\n6. **Review Results** - See how the feedback system works\n7. **Explore Features** - Try Exam Analyzer and Flashcards\n8. **Check Dashboard** - View your progress and statistics\n9. **Customize Profile** - Add your information and picture\n\n**First Session Tips:**\n• Start with a small file to get familiar\n• Try both quiz types (MCQ and short answer)\n• Explore the dashboard features\n• Don\'t worry about perfect scores - it\'s learning!\n\n**What to Upload First:**\n• Lecture notes or slides\n• Textbook chapters\n• Study guides\n• Any educational content\n\nReady to transform your studying? Let\'s go! 📚✨',
                'keywords': 'get started, how to use, setup, begin, start, first steps'
            },
            {
                'category': 'file_types',
                'question': 'What file types does Lamla AI support?',
                'answer': 'Lamla AI supports a variety of file formats to make uploading easy! 📄\n\n**Supported File Types:**\n• **PDF Documents** (.pdf)\n  - Lecture notes and slides\n  - Textbooks and research papers\n  - Study guides and handouts\n\n• **PowerPoint Presentations** (.pptx)\n  - Slides and presentations\n  - Educational content\n  - Visual materials\n\n• **Text Files** (.txt)\n  - Notes and summaries\n  - Study materials\n  - Any text content\n\n**Upload Options:**\n• **File Upload** - Select files from your device\n• **Drag & Drop** - Simply drag files into the upload area\n• **Text Pasting** - Copy and paste text directly\n\n**File Requirements:**\n• **Maximum Size** - 10MB per file\n• **Text Content** - Must contain readable text\n• **Quality** - Clear, well-formatted documents work best\n\n**Pro Tips:**\n• Use clear, readable documents\n• Avoid scanned images without text\n• Combine multiple files for comprehensive coverage\n• Ensure text is properly formatted\n\nYour content, our AI - perfect match! 🤝',
                'keywords': 'file types, supported files, upload formats, documents, pdf, pptx, txt'
            },
            {
                'category': 'quiz_generation',
                'question': 'How does quiz generation work?',
                'answer': 'Our AI quiz generation is like having a personal tutor! 🧠\n\n**Quiz Generation Process:**\n1. **Upload Materials** - Add your study files (PDF, PPTX, or text)\n2. **AI Analysis** - Our AI reads and understands your content\n3. **Question Creation** - Generates relevant questions:\n   • **Multiple Choice** - 4 options (A, B, C, D)\n   • **Short Answer** - Open-ended questions\n4. **Answer Generation** - Provides correct answers and explanations\n5. **Customization** - You choose number of questions and time limit\n6. **Personalization** - Questions based solely on your content\n\n**AI Technology:**\n• **Advanced NLP** - Natural language processing\n• **Content Understanding** - Grasps key concepts\n• **Educational Focus** - Designed for learning\n• **Quality Control** - Ensures relevant questions\n\n**Question Types:**\n• **Multiple Choice** - Test knowledge and recall\n• **Short Answer** - Assess deeper understanding\n• **Explanations** - Learn why answers are correct\n\n**Customization Options:**\n• Number of questions per type\n• Time limits\n• Difficulty adjustment\n• Content focus areas\n\nYour materials, your questions, your learning! 📝',
                'keywords': 'quiz generation, how quizzes work, question creation, AI questions, multiple choice'
            },
            {
                'category': 'flashcards',
                'question': 'How do flashcards help with studying?',
                'answer': 'Flashcards are a proven study method that works! 🗂️\n\n**How Flashcards Help:**\n• **Active Recall** - Testing your memory strengthens it\n• **Spaced Repetition** - Review at optimal intervals\n• **Concept Reinforcement** - Focus on key ideas\n• **Visual Learning** - See information clearly\n• **Quick Review** - Perfect for short study sessions\n\n**Flashcard Types Available:**\n• **General** - Mixed content from your materials\n• **Concepts** - Terms, definitions, and key ideas\n• **Processes** - Step-by-step procedures and sequences\n\n**Study Techniques:**\n1. **Test Yourself** - Try to answer before flipping\n2. **Review Regularly** - Use spaced repetition\n3. **Focus on Weak Areas** - Mark cards you need to review\n4. **Group Related Cards** - Study similar concepts together\n5. **Use Visual Cues** - Add images or diagrams if helpful\n\n**Benefits:**\n• **Memory Retention** - Information sticks better\n• **Confidence Building** - See your progress\n• **Efficient Learning** - Study smarter, not longer\n• **Portable** - Study anywhere, anytime\n\n**Pro Tips:**\n• Review cards you got wrong more frequently\n• Create your own study schedule\n• Combine with other study methods\n• Track your progress\n\nTransform your studying with flashcards! 📚✨',
                'keywords': 'flashcards, study tool, learning, memory, recall, spaced repetition'
            },
            {
                'category': 'pricing',
                'question': 'Is Lamla AI free to use?',
                'answer': 'Lamla AI is designed to be accessible to all students! 💰\n\n**Current Access:**\n• **Free Features** - Core functionality available\n• **Premium Options** - Enhanced features available\n• **Student-Friendly** - Designed for affordability\n\n**What\'s Available:**\n• **Basic Features** - Quiz generation, flashcards, basic analytics\n• **Core Tools** - File upload, question creation, results\n• **Platform Access** - Dashboard, profile, support\n\n**For Specific Pricing:**\n• Contact support@lamla.ai\n• Inquire about premium features\n• Learn about student discounts\n• Get personalized information\n\n**Our Commitment:**\n• **Accessibility** - Quality education for all\n• **Transparency** - Clear pricing information\n• **Student Focus** - Designed for learners\n• **Value** - Worth every penny invested\n\n**Contact Us:**\n• Email: support@lamla.ai\n• Ask about current offers\n• Learn about premium features\n• Get personalized pricing\n\nEducation should be accessible! 📚',
                'keywords': 'free, pricing, cost, subscription, payment, accessibility'
            },
            {
                'category': 'subjects',
                'question': 'What subjects does Lamla AI support?',
                'answer': 'Lamla AI supports ANY subject because we work with YOUR materials! 📚\n\n**Universal Support:**\n• **Science** - Biology, Chemistry, Physics, etc.\n• **Mathematics** - Algebra, Calculus, Statistics, etc.\n• **Literature** - English, Poetry, Novels, etc.\n• **History** - World History, Political Science, etc.\n• **Business** - Economics, Management, Marketing, etc.\n• **Medicine** - Anatomy, Physiology, Pharmacology, etc.\n• **Engineering** - Mechanical, Electrical, Civil, Computer Science etc.\n• **Languages** - Spanish, French, German, etc.\n• **Arts** - Music, Visual Arts, Theater, etc.\n• **Any Academic Subject** - Whatever you\'re studying!\n\n**How It Works:**\n• **Your Content** - Upload your specific study materials\n• **AI Adaptation** - Our AI adapts to your subject\n• **Personalized Questions** - Based on your content\n• **Subject-Specific** - Questions match your field\n\n**Why It Works for All Subjects:**\n• **Content-Based** - Works with any text material\n• **Flexible AI** - Adapts to different subjects\n• **Personalized** - Your materials, your questions\n• **Comprehensive** - Covers all academic levels\n\n**Academic Levels:**\n• High School\n• University/College\n• Graduate Studies\n• Professional Development\n• Self-Study\n\nNo subject is too specific or too broad! 🎓',
                'keywords': 'subjects, topics, courses, academic, study areas, any subject'
            },
            {
                'category': 'difference',
                'question': 'What makes Lamla AI different from other study tools?',
                'answer': 'Lamla AI is unique because we focus on YOUR learning journey! 🌟\n\n**What Makes Us Different:**\n• **Your Materials** - Uses YOUR actual study content (not generic)\n• **AI Personalization** - Tailored to your specific content\n• **Exam Focus** - Designed for exam preparation\n• **Smart Philosophy** - "Study Smarter. Perform Better."\n• **Comprehensive Tools** - Quizzes, flashcards, and analytics\n• **Student-Centered** - Built specifically for students\n• **Quality Explanations** - Detailed feedback and insights\n• **Progress Tracking** - Monitor your improvement over time\n\n**Unique Features:**\n• **Content-Based Generation** - Questions from your materials\n• **Multiple AI Models** - Azure OpenAI, Google Gemini, Hugging Face\n• **Educational Focus** - Designed for learning, not just testing\n• **Comprehensive Analytics** - Detailed performance insights\n• **User-Friendly Design** - Intuitive and accessible\n\n**Our Approach:**\n• **Personalized Learning** - Your content, your questions\n• **Active Engagement** - Interactive study methods\n• **Continuous Improvement** - Learn from your performance\n• **Supportive Environment** - Encouraging and helpful\n\n**Why Students Choose Us:**\n• **Relevance** - Questions match your actual content\n• **Effectiveness** - Proven study methods\n• **Convenience** - All-in-one platform\n• **Results** - Better exam performance\n\nWe\'re not just another study tool - we\'re your learning partner! 🤝',
                'keywords': 'different, unique, better, advantages, comparison, personalization'
            },
            {
                'category': 'contact',
                'question': 'How can I contact Lamla AI support?',
                'answer': 'We\'re here to help you succeed! Here are all the ways to reach us: 📞\n\n**Contact Methods:**\n• **WhatsApp/Direct Call** - +233509341251\n• **Email Support** - contact.lamla1@gmail.com (redirects to contact.lamla1@gmail.com)\n• **Contact Page** - Use the form on our website\n• **Feedback System** - Submit after taking quizzes\n• **About Page** - Contact form available\n• **AI Assistant** - That\'s me! Ask me anything\n\n**What We Help With:**\n• **Technical Issues** - Platform problems and bugs\n• **Feature Questions** - How to use our tools\n• **Account Issues** - Login, profile, settings\n• **General Inquiries** - Any questions about Lamla AI\n• **Feedback** - Suggestions and improvements\n• **Pricing** - Information about plans and features\n\n**Response Times:**\n• **AI Assistant** - Instant responses (that\'s me!)\n• **Email Support** - Within 24 hours\n• **Contact Forms** - Within 48 hours\n\n**Before Contacting:**\n• Try the AI assistant first (me!)\n• Check our FAQ sections\n• Be specific about your issue\n• Include relevant details\n\n**We\'re Committed To:**\n• **Quick Responses** - Get help when you need it\n• **Quality Support** - Thorough and helpful answers\n• **Student Success** - Your learning is our priority\n• **Continuous Improvement** - Your feedback matters\n\nDon\'t hesitate to reach out - we\'re here for you! 💪',
                'keywords': 'contact, support, help, email, assistance, feedback'
            },
            {
                'category': 'target_audience',
                'question': 'Who is Lamla AI designed for?',
                'answer': 'Lamla AI is designed for students who want to study smarter! 🎓\n\n**Our Target Audience:**\n• **High School Students** - Preparing for exams and tests\n• **University Students** - Studying for courses and assessments\n• **Graduate Students** - Advanced academic preparation\n• **Professional Students** - Continuing education and certifications\n• **Self-Learners** - Anyone pursuing knowledge\n• **International Students** - Starting in Africa, available worldwide\n\n**Perfect For Students Who:**\n• Want to study more effectively\n• Prefer personalized study materials\n• Need structured exam preparation\n• Value detailed feedback and explanations\n• Want to track their progress\n• Believe in "Study Smarter. Perform Better."\n\n**Learning Styles Supported:**\n• **Visual Learners** - Flashcards and visual content\n• **Active Learners** - Interactive quizzes and engagement\n• **Analytical Learners** - Detailed feedback and analytics\n• **Self-Paced Learners** - Study at your own speed\n\n**Academic Levels:**\n• **Secondary Education** - High school and equivalent\n• **Higher Education** - University and college\n• **Graduate Studies** - Master\'s and PhD programs\n• **Professional Development** - Certifications and training\n\n**Geographic Reach:**\n• **Started in Africa** - Designed for African students\n• **Global Availability** - Accessible worldwide\n• **Cultural Sensitivity** - Respects diverse learning styles\n• **Language Support** - Works with multiple languages\n\n**Our Philosophy:**\n• **Inclusive Design** - Accessible to all students\n• **Quality Education** - No compromise on learning quality\n• **Student Success** - Your achievement is our goal\n• **Continuous Support** - We\'re here throughout your journey\n\nIf you\'re a student who wants to excel, Lamla AI is for you! 🚀',
                'keywords': 'who is it for, target audience, students, learners, users, high school, university'
            },
            {
                'category': 'mission',
                'question': 'What is Lamla AI\'s mission?',
                'answer': 'Our mission is "Study Smarter. Perform Better." - and we live by it every day! 🎯\n\n**Core Mission:**\nWe believe in transforming how students approach learning by replacing guesswork with guided, personalized study experiences.\n\n**What We Believe:**\n• **Guided Learning** - Replace guesswork with structured study\n• **AI-Powered Insights** - Use technology to enhance learning\n• **Performance Focus** - Real-time feedback for improvement\n• **Smart Preparation** - Be a compass, not just a tool\n• **Comprehensive Support** - Full study assistant, not shortcuts\n• **Intentional Study** - Study with purpose, not panic\n\n**Our Approach:**\n• **Personalized Content** - Your materials, your questions\n• **Active Engagement** - Interactive learning methods\n• **Continuous Feedback** - Learn from every interaction\n• **Progress Tracking** - See your improvement over time\n• **Quality Education** - No compromise on learning standards\n\n**Student Success Focus:**\n• **Confidence Building** - Help students believe in themselves\n• **Skill Development** - Build effective study habits\n• **Knowledge Retention** - Ensure learning sticks\n• **Exam Readiness** - Prepare for success\n• **Lifelong Learning** - Develop love for learning\n\n**Our Commitment:**\n• **Accessibility** - Quality education for all students\n• **Innovation** - Continuous platform improvement\n• **Support** - Always here to help\n• **Excellence** - Strive for the best learning experience\n\n**Vision:**\nTo become the leading AI-powered study companion that helps students worldwide achieve their academic goals through intelligent, personalized learning experiences.\n\nWe\'re not just a tool - we\'re your learning partner! 🤝',
                'keywords': 'mission, purpose, goal, philosophy, approach, study smarter'
            },
            {
                'category': 'performance_tracking',
                'question': 'How does performance tracking work?',
                'answer': 'Performance tracking helps you see your progress and improve! 📊\n\n**What We Track:**\n• **Quiz Scores** - Percentage and raw scores\n• **Question Analysis** - Correct vs. incorrect answers\n• **Progress Over Time** - Improvement trends\n• **Weak Areas** - Topics needing more focus\n• **Study Sessions** - Frequency and duration\n• **Feedback Submissions** - Your engagement level\n• **Dashboard Statistics** - Comprehensive overview\n• **Performance Analytics** - Visual charts and insights\n\n**Tracking Features:**\n• **Real-Time Updates** - See results immediately\n• **Historical Data** - Track progress over time\n• **Visual Charts** - Easy-to-understand graphs\n• **Detailed Breakdowns** - Question-by-question analysis\n• **Improvement Suggestions** - Areas to focus on\n• **Performance Trends** - See your learning curve\n\n**Where to View:**\n• **Dashboard** - Main performance overview\n• **Profile Page** - Personal statistics\n• **Quiz Results** - Immediate feedback\n• **Analytics Section** - Detailed insights\n\n**Benefits:**\n• **Motivation** - See your improvement\n• **Focus** - Identify weak areas\n• **Planning** - Plan study sessions better\n• **Confidence** - Build self-assurance\n• **Goal Setting** - Set realistic targets\n\n**Pro Tips:**\n• Check your dashboard regularly\n• Review weak areas for improvement\n• Celebrate progress milestones\n• Use data to plan study sessions\n• Track long-term trends\n\nYour success story, visualized! 📈✨',
                'keywords': 'performance tracking, analytics, progress, scores, results, improvement'
            },
            {
                'category': 'ai_technology',
                'question': 'What AI technology does Lamla AI use?',
                'answer': 'Lamla AI uses cutting-edge AI technology to power your learning! 🤖\n\n**AI Technologies:**\n• **Azure OpenAI** - Advanced language processing and generation\n• **Google Gemini** - Content generation and analysis\n• **Hugging Face Models** - Additional AI capabilities\n• **Custom Algorithms** - Educational content analysis\n• **Natural Language Processing** - Understanding educational materials\n\n**AI Capabilities:**\n• **Content Understanding** - Reads and comprehends study materials\n• **Question Generation** - Creates relevant educational questions\n• **Answer Analysis** - Provides detailed explanations\n• **Personalization** - Adapts to your specific content\n• **Quality Control** - Ensures educational value\n• **Multi-Model Approach** - Redundancy and reliability\n\n**Educational Focus:**\n• **Subject-Specific** - Adapts to different academic fields\n• **Level-Appropriate** - Matches your academic level\n• **Learning-Oriented** - Designed for education, not just testing\n• **Feedback-Rich** - Provides detailed explanations\n• **Progress-Aware** - Tracks and adapts to your learning\n\n**Technology Benefits:**\n• **Reliability** - Multiple AI models for consistency\n• **Accuracy** - High-quality question generation\n• **Speed** - Fast processing and response times\n• **Scalability** - Handles various content types\n• **Security** - Secure data processing\n\n**AI Features:**\n• **Smart Content Analysis** - Understands your materials\n• **Intelligent Question Creation** - Relevant and challenging\n• **Detailed Explanations** - Learn why answers are correct\n• **Personalized Learning** - Adapts to your needs\n• **Continuous Improvement** - Gets better with use\n\nPowered by the latest AI technology! 🚀',
                'keywords': 'AI technology, artificial intelligence, models, algorithms, Azure OpenAI, Gemini'
            },
            {
                'category': 'privacy',
                'question': 'How does Lamla AI protect my data?',
                'answer': 'Your privacy and data security are our top priorities! 🔒\n\n**Data Protection Measures:**\n• **Industry-Standard Security** - Enterprise-level protection\n• **Secure File Processing** - Your materials are handled safely\n• **Privacy Protection** - Personal data never shared with third parties\n• **Educational Use Only** - Data used solely for learning experiences\n• **Secure Uploads** - Protected file transfer and storage\n• **Access Controls** - Only you can access your data\n• **Regular Audits** - Continuous security monitoring\n\n**What We Protect:**\n• **Study Materials** - Your uploaded files and content\n• **Personal Information** - Name, email, profile data\n• **Study History** - Quiz results and progress\n• **Account Data** - Login credentials and preferences\n• **Feedback** - Your comments and suggestions\n\n**Privacy Commitments:**\n• **No Third-Party Sharing** - Your data stays with us\n• **Educational Purpose Only** - Used for learning enhancement\n• **User Control** - You control your data\n• **Transparency** - Clear privacy policy available\n• **Compliance** - Follow data protection regulations\n\n**Security Features:**\n• **Encrypted Storage** - Data protected at rest\n• **Secure Transmission** - Protected data transfer\n• **Access Authentication** - Secure login systems\n• **Regular Backups** - Data safety and recovery\n• **Monitoring** - Continuous security oversight\n\n**Your Rights:**\n• **Data Access** - View your stored information\n• **Data Deletion** - Remove your data when needed\n• **Privacy Inquiries** - Contact us with concerns\n• **Policy Review** - Read our privacy policy\n• **Control** - Manage your privacy settings\n\n**Contact for Privacy:**\n• Email: support@lamla.ai\n• Privacy Policy: Available on website\n• Questions: We\'re here to help\n\nYour privacy matters to us! 🛡️',
                'keywords': 'privacy, data protection, security, confidentiality, personal data'
            }
        ]
        
        # Create knowledge base entries
        created_count = 0
        for entry in knowledge_entries:
            ChatbotKnowledge.objects.create(
                category=entry['category'],
                question=entry['question'],
                answer=entry['answer'],
                keywords=entry['keywords'],
                is_active=True
            )
            created_count += 1
            self.stdout.write(f"Created: {entry['question']}")
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} knowledge base entries!')
        ) 