from flask import Flask, render_template, request, send_file, redirect, url_for
from urllib.parse import urlparse
from engine.tracker_analyzer import analyze_website, classify_trackers, save_csv
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.form['url']
    domain = urlparse(url).netloc.replace("www.", "")
    return render_template('loading.html', domain=domain, url=url)

@app.route('/report/<domain>')
def show_report(domain):
    url = f"https://{domain}"  # Assuming https; adjust if needed

    # Run analysis
    accept_log = analyze_website(url, "accept")
    reject_log = analyze_website(url, "reject")

    # Classify trackers
    accept_trackers = classify_trackers(accept_log, domain)
    reject_trackers = classify_trackers(reject_log, domain)

    # Find common trackers
    common = {
        "ads": list(set(accept_trackers["ads"]) & set(reject_trackers["ads"])),
        "analytics": list(set(accept_trackers["analytics"]) & set(reject_trackers["analytics"])),
        "social": list(set(accept_trackers["social"]) & set(reject_trackers["social"])),
        "performance": list(set(accept_trackers["performance"]) & set(reject_trackers["performance"]))
    }

    # Count data
    accept_count = {k: len(v) for k, v in accept_trackers.items()}
    reject_count = {k: len(v) for k, v in reject_trackers.items()}
    common_count = {k: len(v) for k, v in common.items()}

    # Ensure output directory exists
    os.makedirs("csv_outputs", exist_ok=True)

    # Save CSV
    csv_data = {
        'accept_ads': accept_trackers['ads'],
        'accept_analytics': accept_trackers['analytics'],
        'accept_social': accept_trackers['social'],
        'accept_performance': accept_trackers['performance'],
        'reject_ads': reject_trackers['ads'],
        'reject_analytics': reject_trackers['analytics'],
        'reject_social': reject_trackers['social'],
        'reject_performance': reject_trackers['performance']
    }
    save_csv(csv_data, os.path.join("csv_outputs", f"{domain}_trackers.csv"))

    return render_template(
        "report.html",
        url=url,
        domain=domain,
        accept_count=accept_count,
        reject_count=reject_count,
        common_count=common_count
    )

@app.route('/download/<domain>')
def download_csv(domain):
    filepath = os.path.join("csv_outputs", f"{domain}_trackers.csv")
    if not os.path.exists(filepath):
        return f"CSV report for {domain} not found.", 404
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
