# app/routes/google.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, jsonify
from flask_login import login_required
from app.models import db, DiscoveredSite, ManualSite, CommentLog, ScheduledTask
from app.utils.serper_search import find_comment_enabled_sites
from app.comment_bot import post_comment
from app.utils.moz import get_domain_authority
import csv
import io
from datetime import datetime
import os
from sqlalchemy import func
from apscheduler.schedulers.background import BackgroundScheduler
from urllib.parse import urlparse
from flask import current_app
from app.utils.openpagerank import get_opr_score
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
from app.utils.scrapfly_search import search_google
from app.utils.comment_phrases import COMMENT_PHRASES


scheduler = BackgroundScheduler()

def start_scheduler():
    if not scheduler.running:
        scheduler.start()

def build_search_query(keyword, lang):
    phrase = COMMENT_PHRASES.get(lang, "")
    if phrase:
        return f'{keyword} "{phrase}"'
    return keyword

def has_comment_form(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        time.sleep(3)
        driver.find_element(By.NAME, "author")
        driver.find_element(By.NAME, "email")
        driver.find_element(By.NAME, "comment")
        return True
    except NoSuchElementException:
        return False
    except:
        return False
    finally:
        driver.quit()

google_bp = Blueprint('google', __name__)
scheduler = BackgroundScheduler()
scheduler.start()


def run_scheduled_tasks():
    from app import create_app
    app = create_app()
    with app.app_context():
        now = datetime.utcnow()
        tasks = ScheduledTask.query.filter_by(is_active=True).all()
        for task in tasks:
            if not task.last_run or (now - task.last_run).total_seconds() >= task.interval_minutes * 60:
                found_sites = find_comment_enabled_sites(task.keyword, task.pages, task.language)
                for site in found_sites:
                    if not DiscoveredSite.query.filter_by(url=site).first():
                        domain = urlparse(site).netloc
                        da_score = get_opr_score(domain)
                        minPageRank = current_app.config['MIN_PAGE_RANK']

                        if da_score and da_score >= minPageRank and has_comment_form(site):
                            new_site = DiscoveredSite(
                                url=site,
                                keyword=task.keyword,
                                language=task.language,
                                page_rank=da_score
                            )
                            db.session.add(new_site)
                            db.session.flush()

                            result = post_comment(site)
                            log = CommentLog(
                                site_id=new_site.id,
                                url=site,
                                status='success' if result['success'] else 'failed',
                                screenshot_path=result.get('screenshot')
                            )
                            db.session.add(log)
                task.last_run = now
        db.session.commit()
scheduler.add_job(run_scheduled_tasks, 'interval', minutes=1)


@google_bp.route('/google-search', methods=['GET', 'POST'])
@login_required
def google_search():
    if request.method == 'POST':
        keyword = request.form.get('keyword')
        pages = int(request.form.get('pages'))
        lang = request.form.get('lang')

        found_sites = find_comment_enabled_sites(keyword, pages, lang)

        for site in found_sites:
            if not DiscoveredSite.query.filter_by(url=site).first():
                domain = urlparse(site).netloc
                da_score = get_opr_score(domain)
                minPageRank = current_app.config['MIN_PAGE_RANK']

                if da_score and da_score >= minPageRank and has_comment_form(site):
                    db.session.add(DiscoveredSite(url=site, keyword=keyword, language=lang, page_rank=da_score))
        db.session.commit()

        flash(f"{len(found_sites)} site bulundu ve kaydedildi.")
        return redirect(url_for('google.google_search'))

    sites = DiscoveredSite.query.order_by(DiscoveredSite.id.desc()).limit(50).all()
    return render_template('google_search.html', sites=sites)


@google_bp.route('/google-search/export')
@login_required
def export_csv():
    sites = DiscoveredSite.query.order_by(DiscoveredSite.id.desc()).all()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['URL', 'Anahtar Kelime', 'Dil', 'DA'])
    for site in sites:
        cw.writerow([site.url, site.keyword, site.language, site.domain_authority or ''])
    output = si.getvalue()
    return Response(
        output,
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=discovered_sites.csv"}
    )


@google_bp.route('/google-search/blacklist/<int:id>', methods=['POST'])
@login_required
def add_to_blacklist(id):
    site = DiscoveredSite.query.get_or_404(id)
    if not ManualSite.query.filter_by(url=site.url).first():
        db.session.add(ManualSite(url=site.url))
    db.session.delete(site)
    db.session.commit()
    flash(f"{site.url} kara listeye eklendi ve listeden çıkarıldı.")
    return redirect(url_for('google.google_search'))


@google_bp.route('/google-search/submit/<int:id>', methods=['POST'])
@login_required
def submit_comment(id):
    site = DiscoveredSite.query.get_or_404(id)
    success, screenshot = post_comment(site.url)

    log = CommentLog(
        site_id=site.id,
        url=site.url,
        status="success" if success else "failed",
        screenshot_path=screenshot if screenshot else None,
        timestamp=datetime.utcnow()
    )
    db.session.add(log)
    db.session.commit()

    if success:
        flash(f"✅ Yorum gönderildi: {site.url}")
    else:
        flash(f"❌ Yorum gönderilemedi: {site.url}")

    return redirect(url_for('google.google_search'))


@google_bp.route('/logs', methods=['GET', 'POST'])
@login_required
def logs():
    if request.method == 'POST':
        return redirect(url_for('google.retry_failed_comments'))

    query = CommentLog.query.order_by(CommentLog.timestamp.desc())

    status_filter = request.args.get('status')
    keyword_filter = request.args.get('keyword')
    if status_filter in ['success', 'failed']:
        query = query.filter(CommentLog.status == status_filter)
    if keyword_filter:
        query = query.filter(CommentLog.url.ilike(f"%{keyword_filter}%"))

    log_records = query.limit(100).all()
    return render_template('logs.html', logs=log_records, status_filter=status_filter, keyword_filter=keyword_filter)


@google_bp.route('/logs/chart')
@login_required
def logs_chart():
    data = db.session.query(
        func.date(CommentLog.timestamp),
        CommentLog.status,
        func.count(CommentLog.id)
    ).group_by(func.date(CommentLog.timestamp), CommentLog.status).all()

    result = {}
    for date, status, count in data:
        date_str = date.strftime('%Y-%m-%d')
        if date_str not in result:
            result[date_str] = {'success': 0, 'failed': 0}
        result[date_str][status] = count

    labels = sorted(result.keys())
    success_counts = [result[date]['success'] for date in labels]
    failed_counts = [result[date]['failed'] for date in labels]

    return render_template('logs_chart.html', labels=labels, success=success_counts, failed=failed_counts)


@google_bp.route('/logs/retry-failed', methods=['POST'])
@login_required
def retry_failed_comments():
    failed_logs = CommentLog.query.filter_by(status='failed').order_by(CommentLog.timestamp.desc()).limit(100).all()
    retried = 0
    for log in failed_logs:
        success, screenshot = post_comment(log.url)
        new_log = CommentLog(
            site_id=log.site_id,
            url=log.url,
            status="success" if success else "failed",
            screenshot_path=screenshot if screenshot else None,
            timestamp=datetime.utcnow()
        )
        db.session.add(new_log)
        retried += 1
    db.session.commit()
    flash(f"{retried} başarısız giriş yeniden denendi.")
    return redirect(url_for('google.logs'))


@google_bp.route('/logs/export-success')
@login_required
def export_success_logs():
    return _export_logs_by_status('success', 'success_logs.csv')


@google_bp.route('/logs/export-failed')
@login_required
def export_failed_logs():
    return _export_logs_by_status('failed', 'failed_logs.csv')


def _export_logs_by_status(status, filename):
    logs = CommentLog.query.filter_by(status=status).order_by(CommentLog.timestamp.desc()).all()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Tarih', 'URL', 'Durum', 'Ekran Görüntüsü'])
    for log in logs:
        cw.writerow([
            log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            log.url,
            log.status,
            log.screenshot_path or '-'
        ])
    output = si.getvalue()
    return Response(
        output,
        mimetype='text/csv',
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )


@google_bp.route('/scheduler')
@login_required
def scheduler_panel():
    tasks = ScheduledTask.query.order_by(ScheduledTask.id.desc()).all()
    return render_template('scheduler.html', tasks=tasks)


@google_bp.route('/scheduler', methods=['POST'])
@login_required
def scheduler_add():
    keyword = request.form.get('keyword')
    language = request.form.get('language')
    pages = int(request.form.get('pages'))
    interval = int(request.form.get('interval'))

    task = ScheduledTask(
        keyword=keyword,
        language=language,
        pages=pages,
        interval_minutes=interval,
        last_run=None,
        is_active=True
    )
    db.session.add(task)
    db.session.commit()
    flash("Zamanlanmış görev başarıyla eklendi.")
    return redirect(url_for('google.scheduler_panel'))


@google_bp.route('/scheduler/toggle/<int:task_id>', methods=['POST'])
@login_required
def scheduler_toggle(task_id):
    task = ScheduledTask.query.get_or_404(task_id)
    task.is_active = not task.is_active
    db.session.commit()
    flash("Görev durumu güncellendi.")
    return redirect(url_for('google.scheduler_panel'))


@google_bp.route('/scheduler/delete/<int:task_id>', methods=['POST'])
@login_required
def scheduler_delete(task_id):
    task = ScheduledTask.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash("Görev silindi.")
    return redirect(url_for('google.scheduler_panel'))


@google_bp.route('/manual-sites', methods=['GET', 'POST'])
@login_required
def manual_sites():
    if request.method == 'POST':
        url = request.form.get('url')
        keyword = request.form.get('keyword')
        language = request.form.get('language')

        if not ManualSite.query.filter_by(url=url).first():
            if has_comment_form(url):
                domain = urlparse(url).netloc
                da_score = get_opr_score(domain)
                minPageRank = current_app.config['MIN_PAGE_RANK']

                if da_score and da_score >= minPageRank:
                    new_site = ManualSite(url=url, keyword=keyword, language=language, page_rank=da_score)
                    db.session.add(new_site)
                    db.session.commit()
                    flash("Manuel site eklendi.", "success")
                else:
                    flash("Page Rank sınırın altında olduğu için eklenmedi.", "warning")
            else:
                flash("Yorum formu bulunamadı, eklenmedi.", "warning")
        else:
            flash("Bu URL zaten mevcut.", "warning")
        return redirect(url_for('google.manual_sites'))

    sites = ManualSite.query.order_by(ManualSite.id.desc()).all()
    return render_template('manual_sites.html', sites=sites)


@google_bp.route('/google-search/step')
@login_required
def google_search_step():
    from urllib.parse import urlparse
    import json
    keyword = request.args.get('keyword')
    lang = request.args.get('lang', 'en')
    page = int(request.args.get('page', 0))

    sites = find_comment_enabled_sites(keyword, lang=lang, page_limit=1)

    added_count = 0
    log_details = []

    for item in sites:
        url = item["url"] if isinstance(item, dict) else item
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        domain = urlparse(url).netloc
        minPageRank = current_app.config['MIN_PAGE_RANK']

        page_rank = get_opr_score(domain)
        has_form = has_comment_form(url)

        log_entry = {
            "url": url,
            "title": title,
            "snippet": snippet,
            "page_rank": page_rank,
            "has_comment_form": has_form,
            "status": "❌ Eklenmedi"
        }

        print("🔍 Gelen site bilgisi:")
        print(json.dumps(log_entry, indent=2, ensure_ascii=False))

        if page_rank is None or page_rank < minPageRank:
            log_entry["status"] = "🔻 Düşük Page Rank"
        elif not has_form:
            log_entry["status"] = "💬 Yorum Formu Yok"
        elif DiscoveredSite.query.filter_by(url=url).first():
            log_entry["status"] = "⚠️ Zaten Mevcut"
        else:
            new_site = DiscoveredSite(
                url=url,
                keyword=keyword,
                language=lang,
                page_rank=page_rank,
                has_comment_form=has_form
            )
            db.session.add(new_site)
            added_count += 1
            log_entry["status"] = "✅ Eklendi"

        log_details.append(log_entry)

    db.session.commit()

    return jsonify({
        "added": added_count,
        "log_details": log_details,
        "keyword": keyword,
        "lang": lang
    })




@google_bp.route('/google-search/history')
@login_required
def google_search_history():
    keywords = db.session.query(
        DiscoveredSite.keyword,
        DiscoveredSite.language,
        db.func.count(DiscoveredSite.id).label("site_count"),
        db.func.min(DiscoveredSite.created_at).label("first_added"),
        db.func.max(DiscoveredSite.created_at).label("last_added")
    ).group_by(DiscoveredSite.keyword, DiscoveredSite.language).all()

    return render_template('google_search_history.html', keywords=keywords)


@google_bp.route('/google-search/restart', methods=['POST'])
@login_required
def google_search_restart():
    keyword = request.form.get('keyword')
    lang = request.form.get('lang')
    pages = int(request.form.get('pages'))

    for page in range(pages):
        find_comment_enabled_sites(keyword, 1, lang, start_offset=page * 10)

    flash("Arama yeniden başlatıldı!")
    return redirect(url_for('google.google_search_history'))


@google_bp.route('/google-search/fetch-latest')
@login_required
def fetch_latest_sites():
    sites = DiscoveredSite.query.order_by(DiscoveredSite.created_at.desc()).limit(20).all()
    return render_template('partials/latest_sites.html', sites=sites)

@google_bp.route('/discovered-sites')
@login_required
def get_discovered_sites():
    from app.models import DiscoveredSite  # gerekiyorsa içe aktar
    sites = DiscoveredSite.query.order_by(DiscoveredSite.created_at.desc()).limit(100).all()

    return jsonify([
        {
            "url": site.url,
            "keyword": site.keyword,
            "language": site.language,
            "page_rank": site.page_rank
        }
        for site in sites
    ])
