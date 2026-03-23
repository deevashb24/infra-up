# Uttar Pradesh Infrastructure Data Pipeline Design

## Overview
This document outlines the architecture for a centralized, automated data ingestion pipeline specifically designed to scrape, standardize, and verify infrastructure project data from various Uttar Pradesh civic and state-level endpoints.

## 1. Data Sources & Ingestion Methods

### A. API Integrations
* **data.gov.in**
  * **Method:** REST API (OGD Platform India)
  * **Target:** Filter for datasets dynamically tagged `Uttar Pradesh` AND (`infrastructure` OR `roads`).
  * **Frequency:** Weekly cron job.

### B. Specialized Web Scrapers (Python / Scrapy / Playwright)
Many regional UP portals lack modern APIs and require headless browsing or HTML scraping to extract project tables, PDFs, and active tender documents.
* **Lucknow Smart City (lucknowsmartcity.com):** 
  * **Target:** Project tracker dashboards (ABD & PAN city projects).
* **NHAI (nhai.gov.in):** 
  * **Target:** "Project Implementation Unit (PIU)" dashboards explicitly filtered for `Uttar Pradesh`.
* **UP Public Works Dept (uppwd.gov.in):** 
  * **Target:** Ongoing state highway and major district road (MDR) tenders and progress reports.
* **Lucknow Municipal Corporation (lmc.up.nic.in):** 
  * **Target:** Civic works, road repairs, and zone-wise development updates.
* **Lucknow Development Authority (lda.up.nic.in):** 
  * **Target:** Housing schemes, commercial complexes, and master plan infrastructure.
* **Jal Nigam UP (upjn.org):** 
  * **Target:** Water supply networks, sewerage treatments, and pipeline projects.

## 2. Standardization Layer (ETL)

Raw data scraped from these 7 discrete endpoints will arrive in vastly varying formats (JSON, CSV, HTML Tables). An ETL (Extract, Transform, Load) microservice processes this into a unified schema natively matching our PostGIS `infrastructure_projects` table.

### Mapping Strategy
* **`id`**: Generate reproducible UUID (e.g., `uuid5` based on source URL + internal tender ID) to prevent ingestion overlaps.
* **`title`**: Cleaned string (e.g., stripping internal tender codes and boilerplate text).
* **`permit_type`**: NLP classifier mapping keywords (e.g., "pipeline", "sewer" -> `UTILITY`; "highway", "repair" -> `ROAD`; "housing", "complex" -> `CONSTRUCTION`).
* **`project_authority`**: Mapped dynamically from the scraper source (e.g., `upjn.org` -> `Jal Nigam`, `lda.up.nic.in` -> `LDA`).
* **`district`**: Extracted via NLP/Regex from project descriptions or location columns.
* **`geometry`**: 
  * If coordinates natively exist, format as `POINT(lon lat)`.
  * If only text boundaries exist (e.g., "Hazratganj intersection"), pass the string to a Geocoding API constrained strictly to the UP bounding box to derive the exact `[lon, lat]`.

## 3. Deduplication Engine (PostGIS)

Since multiple agencies might report on the exact same structural project (e.g., Smart City and LMC collaborating on an intersection), we aggressively deduplicate before database insertion to prevent map clustering artifacts.

**Algorithm:**
1. **Fuzzy Name Matching:** Use algorithms like Levenshtein distance or pg_trgm (Trigram similarity) natively in Postgres on the `title` field. (Similarity Threshold > 85%).
2. **Geospatial Proximity (`ST_DWithin`):** Check if an existing project in the database lies within a **50-meter radius** of the incoming parsed geometry.
3. **Logic:** If `Fuzzy_Match == TRUE` AND `Geospatial_Proximity == TRUE`, flag as **DUPLICATE** and merge metadata (e.g., retaining the larger budget or updating the `status`), rather than creating a new physical point.

## 4. Manual Review Queue

Because scrapers parse unstructured data or rely on probabilistic Geocoding, some entries will inherently lack confidence.

* **Trigger Conditions:**
  * Geocoding accuracy was low (e.g., resolved broadly to the center of "Lucknow" rather than a precise street).
  * NLP classifier failed to determine a strict `permit_type`.
  * Deduplication similarity was borderline (e.g., 75% title match).
* **Action:** 
  * Insert row into `infrastructure_projects` but set a Boolean column: `is_verified = FALSE`.
* **Admin Dashboard Integration:**
  * In `/dashboard`, authorized government administrators view an "Unverified Projects Queue".
  * Admins can adjust the map pin manually, correct metadata, and click "Approve", which flips `is_verified` to `TRUE`.
  * Only projects where `is_verified = TRUE` are broadcasted to the public `/projects` map feed via our SSE implementation.
