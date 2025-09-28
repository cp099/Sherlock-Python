# Sherlock v2.0: Inventory & Lending Management System

![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)
![Django Version](https://img.shields.io/badge/django-5.1-green.svg)
![License](https://img.shields.io/badge/License-Apache_2.0-yellow.svg)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)

**Sherlock is a comprehensive, self-hosted inventory and lending management system designed for school labs, makerspaces, and workshops.**

This project is a complete, ground-up rewrite and significant feature expansion of the original [Sherlock v1.0](https://github.com/Atal-Lab-DPSBS/Sherlock). It transforms the application from a simple inventory list into a powerful, data-driven lab management platform built on a modern and robust Python/Django backend.

---

### ✨ Features at a Glance

| Command Center Dashboard | Checkout Terminal |
| :---: | :---: |
| ![Dashboard Screenshot](.github/assets/dashboard.png) | ![Checkout Terminal Screenshot](.github/assets/checkout-terminal.png) |
| **Item Detail & Audit Trails** | **On Loan Reporting** |
| ![Item Detail Screenshot](.github/assets/item-detail.png) | ![On Loan Report Screenshot](.github/assets/on-loan-report.png) |

---

## Table of Contents
- [Mission](#-mission)
- [Core Features](#-core-features)
- [Deployment](#-deployment)
- [For Developers: Running from Source](#-for-developers-running-from-source)
- [Technology Stack](#️-technology-stack)
- [License](#️-license)

## 🌟 Mission

The goal of Sherlock v2.0 is to provide a powerful, easy-to-deploy, and intuitive tool for lab managers to track their physical inventory. It answers the critical questions of lab management:
*   **What** do we have and **where** is it?
*   **Who** has borrowed our equipment?
*   **When** is it due back?
*   **What** is our inventory's lifecycle?

## ✨ Core Features

### Inventory Management
*   **Hierarchical Structure:** Organize your inventory logically with **Sections**, **Spaces**, and **Items**.
*   **Stock Control:** A full, permanent audit trail for every stock change (e.g., "Received New Stock," "Reported Damaged").
*   **Label Printing:** Generate and print custom barcode and QR code labels to seamlessly bridge your physical and digital inventory.
*   **Unified Search:** A powerful, live-search dashboard to find any item or student record in the system.

### Advanced Lending System
*   **Student Records:** Maintain a secure database of students with filtering and search capabilities.
*   **Kiosk-Style Checkout Terminal:** A dedicated, fast interface for lending items, featuring a live, as-you-type search for both students and items.
*   **Stock Validation:** The system automatically checks available stock before allowing a checkout.
*   **Partial Returns & Loan History:** A sophisticated check-in system that allows for partial returns and keeps a complete, auditable log of every transaction for both students and items.
*   **Due Date & Overdue Tracking:** Assign a due date to every loan and get instant visibility on overdue items through the main dashboard and a dedicated report.

### Modern Technology
*   **Camera Scanning:** Use your device's camera for rapid checkouts and to instantly look up any item, space, or section with the Universal Scan tool.
*   **Data Visualizations:** The main dashboard features charts for weekly loan activity and most popular items, providing instant insight into your lab's operations.

## 🚀 Deployment

Sherlock is designed for incredibly simple deployment. It is packaged as a **standalone executable** using PyInstaller, containing the entire application, web server, and all dependencies.

### How to Run Sherlock:
1.  Go to the [**Releases**](https://github.com/YOUR-USERNAME/Sherlock-python/releases) page of this repository.
2.  Download the latest `.zip` file for your operating system (e.g., `Sherlock-v2.0.0-Windows.zip`).
3.  Unzip the file and double-click the `Sherlock` executable.

The server will start, automatically creating a new database on the first run. The application will be available at `http://127.0.0.1:8000` and on your local network.

## 💻 For Developers: Running from Source

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/YOUR-USERNAME/Sherlock-python.git
    cd Sherlock-python
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On macOS/Linux
    .\venv\Scripts\activate   # On Windows
    ```
3.  **Install dependencies:** `pip install -r requirements.txt`
4.  **Run migrations:** `python manage.py migrate`
5.  **Create a superuser:** `python manage.py createsuperuser`
6.  **Run the development server:** `python manage.py runserver`

## 🛠️ Technology Stack
*   **Backend:** Python 3, Django
*   **Frontend:** HTML, CSS, HTMX, Chart.js
*   **Server:** Waitress
*   **Packaging:** PyInstaller

## ⚖️ License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for the full license text and the [NOTICE](NOTICE) file for attribution details.