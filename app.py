"""
app.py
Flask application template for the warm-up assignment

Implements the API endpoints for cleaning and analyzing text.
"""

from flask import Flask, request, jsonify, render_template
# IMPORTANT: Rename your preprocessor file to 'preprocess.py'
# or ensure 'starter_preprocess.py' is correctly named.
from starter_preprocess import TextPreprocessor
import traceback
import sys

# Set up the application
app = Flask(__name__)
preprocessor = TextPreprocessor()

# Increase recursion limit for complex processing or deep stack traces if necessary
# sys.setrecursionlimit(2000)


@app.route('/')
def home():
    """Render a simple HTML form for URL input"""
    # This will look for templates/index.html
    return render_template('index.html')


@app.route('/health')
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Text preprocessing service is running"
    })


@app.route('/api/clean', methods=['POST'])
def clean_text():
    """
    API endpoint that accepts a URL, fetches text, cleans it, and returns stats.

    Expected JSON input:
        {"url": "https://www.gutenberg.org/files/1342/1342-0.txt"}

    Returns JSON:
        {
            "success": true/false,
            "cleaned_text": "...",
            "statistics": {...},
            "summary": "...",
            "error": "..." (if applicable)
        }
    """
    try:
        # 1. Get JSON data from request
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'url' field in JSON request."
            }), 400

        url = data['url']

        # 2. Fetch the text
        raw_text = preprocessor.fetch_from_url(url)
        print('working: fetch_from_url')

        # 3. Clean the text (removes Gutenberg markers and leading junk)
        gutenberg_cleaned_text = preprocessor.clean_gutenberg_text(raw_text)
        print('working: gutenberg_clean_text')

        # 4. Normalize the text
        # This step performs lowercasing and punctuation removal.
        # We use the result of this step for everything else (stats, summary, preview).
        normalized_text = preprocessor.normalize_text(
            gutenberg_cleaned_text, preserve_sentences=True)
        print('working: normalized_text')

        # If normalization results in an empty string, we stop here.
        if not normalized_text:
            return jsonify({
                "success": False,
                "error": "The text was cleaned down to nothing. Check your Gutenberg URL or cleaning rules."
            }), 400

        # 5. Get statistics
        statistics = preprocessor.get_text_statistics(normalized_text)
        print('working: statistics')

        # 6. Create summary
        summary = preprocessor.create_summary(normalized_text, num_sentences=3)
        print('working: summary')

        # 7. Return JSON response
        return jsonify({
            "success": True,
            # We return the fully normalized text for the front-end preview
            "cleaned_text": normalized_text,
            "statistics": statistics,
            "summary": summary
        })

    except Exception as e:
        # Use traceback to log the full error for debugging (helpful in the terminal)
        print(f"ERROR in /api/clean: {e}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Text Processing Error: {str(e)}"
        }), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    """
    API endpoint that accepts raw text and returns statistics only

    Expected JSON input:
        {"text": "Your raw text here..."}

    Returns JSON:
        {
            "success": true/false,
            "statistics": {...},
            "error": "..." (if applicable)
        }
    """
    try:
        # 1. Get JSON data from request
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'text' field in request body."
            }), 400

        raw_text = data['text']

        # 2. Clean/Normalize the text (preserving sentences for stats)
        # We don't use clean_gutenberg_text here as it's assumed to be arbitrary raw input
        normalized_text = preprocessor.normalize_text(
            raw_text, preserve_sentences=True)

        # 3. Get statistics with preprocessor.get_text_statistics()
        statistics = preprocessor.get_text_statistics(normalized_text)

        # 4. Return JSON response
        return jsonify({
            "success": True,
            "statistics": statistics
        })

    except Exception as e:
        # Catch exceptions during preprocessing
        print(f"Error in /api/analyze: {e}", file=sys.stderr)
        return jsonify({
            "success": False,
            "error": f"Processing error: {str(e)}"
        }), 500

# Error handlers (these look good, keeping them as they provide nice JSON error responses)


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


if __name__ == '__main__':
    print("🚀 Starting Text Preprocessing Web Service...")
    print("📖 Available endpoints:")
    print("   GET  /        - Web interface")
    print("   GET  /health    - Health check")
    print("   POST /api/clean - Clean text from URL")
    print("   POST /api/analyze - Analyze raw text")
    print()
    print("🌐 Open your browser to: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")

    # Run the app, listening on all interfaces (0.0.0.0) for Codespaces compatibility
    app.run(debug=True, port=5000, host='0.0.0.0')
