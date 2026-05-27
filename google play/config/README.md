# Config — app list for scraping

**Required file:** **`app_list.xlsx`** in this folder.

Columns should include:

- **`app_id`** (required) — Google Play package name  
- **`app_name`** (optional; defaults to `app_id`)  
- **`target_reviews`** (optional; defaults to `500` per app)

Read by `scripts/01_collect/collect_reviews.py` → `find_app_list()`.

---

**Note:** A separate monitoring / drift-check layer was removed from this repo to keep the default path **DA-oriented** (metrics, Memos, SQL, and later BigQuery narrative live on top of the data layer). Historical design notes for that layer remain under the repository root folder **`monitoring layer设计方案/`** (paths are relative to the **repo root**, not to `google play/config/`).
